import os
import math
from fastapi import FastAPI, UploadFile, File, Form
from detection_module import detect_harmful_content
from ocr_module import extract_text_from_image
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
import firebase_admin
from firebase_admin import messaging, credentials
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# ==============================
# Load ENV
# ==============================
load_dotenv()

app = FastAPI(title=os.getenv("APP_NAME", "KiddyGoo AI"))

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://parent-kiddygoo.vercel.app",
        "https://kiddygoo.my.id",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# SECURITY - Bearer Token Middleware
# ==============================
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")


class BearerAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        # Bypass docs, openapi, dan preflight CORS
        if request.method == "OPTIONS":
            return await call_next(request)
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header missing or invalid"}
            )

        token = auth_header.split("Bearer ")[1]
        if token != API_BEARER_TOKEN:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )

        return await call_next(request)


app.add_middleware(BearerAuthMiddleware)

# ==============================
# EMAIL SETUP
# ==============================
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# ==============================
# FIREBASE SETUP
# ==============================
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

# Mock DB untuk simpan device token
DEVICE_TOKENS = set()


# ==============================
# UTIL FUNCTIONS
# ==============================
def send_email_alert(parent_email, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = "⚠️ Notifikasi Bahaya Terdeteksi"
        msg['From'] = SMTP_EMAIL
        msg['To'] = parent_email

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print("Email gagal dikirim:", e)


def send_push_notification(token, message_text):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="⚠️ Bahaya terdeteksi",
                body=message_text,
            ),
            token=token,
        )
        response = messaging.send(message)
        return response
    except Exception as e:
        print("Push notification gagal dikirim:", e)
        return None


# ==============================
# MODELS
# ==============================
class TextInput(BaseModel):
    text: str
    parent_email: str | None = None
    parent_token: str | None = None


class TokenInput(BaseModel):
    token: str


class NotificationInput(BaseModel):
    title: str
    body: str

# ==============================
# API ENDPOINTS
# ==============================


# Simpan device token
@app.post("/api/register-token")
async def register_token(data: TokenInput):
    DEVICE_TOKENS.add(data.token)
    print("Token terdaftar:", data.token)
    return {"success": True, "total_tokens": len(DEVICE_TOKENS)}


# Kirim notifikasi ke semua token
@app.post("/api/send-notification")
async def send_notification(data: NotificationInput):
    responses = []
    for token in DEVICE_TOKENS:
        res = send_push_notification(token, f"{data.title}\n{data.body}")
        responses.append({"token": token, "response": res})
    return {"success": True, "sent": len(responses), "responses": responses}


# Analyze text
@app.post("/analyze-text/")
async def analyze_text(input_data: TextInput):
    result = detect_harmful_content(input_data.text)

    if result["flagged"]:
        confidence_percent = math.ceil(result["confidence"] * 100) 
        alert_msg = (
            f"⚠️ Pesan mencurigakan terdeteksi!\n\n"
            f"Pesan: {result['text']}\n"
            f"Label: {result['label']}\n"
            f"Confidence: {confidence_percent}%\n\n"
            f"Detail Analisis: {result['analysis']}"
        )

        if input_data.parent_email:
            send_email_alert(input_data.parent_email, alert_msg)
        
        if input_data.parent_token:
            send_push_notification(input_data.parent_token, alert_msg)

    return {
        "flagged": result["flagged"],
        "label": result.get("label"),
        "confidence": f"{math.ceil(result['confidence']*100)}%"
    }


# Analyze image
@app.post("/analyze-image/")
async def analyze_image(
    file: UploadFile=File(...),
    parent_email: str=Form(None),
    parent_token: str=Form(None),
):
    text = extract_text_from_image(file.file)
    result = detect_harmful_content(text)

    if result["flagged"]:
        alert_msg = f"Pesan mencurigakan (dari gambar):\n{text}\n\nDetail: {result['analysis']}"
        if parent_email:
            send_email_alert(parent_email, alert_msg)
        if parent_token:
            send_push_notification(parent_token, alert_msg)

    return {"text": text, **result}
