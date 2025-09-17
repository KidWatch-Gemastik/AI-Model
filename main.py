import os
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

# Load ENV
load_dotenv()

app = FastAPI(title=os.getenv("APP_NAME", "KiddyGoo AI"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://parent-kiddygoo.vercel.app",  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- EMAIL SETUP ---
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# --- FIREBASE SETUP ---
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

# Mock DB untuk simpan device token
DEVICE_TOKENS = set()


# Email alert
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


# Push notification
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


# Model untuk input teks
class TextInput(BaseModel):
    text: str
    parent_email: str | None = None
    parent_token: str | None = None

# --- API ENDPOINTS ---


# 1️⃣ Simpan device token
class TokenInput(BaseModel):
    token: str


@app.post("/api/register-token")
async def register_token(data: TokenInput):
    DEVICE_TOKENS.add(data.token)
    print("✅ Token terdaftar:", data.token)
    return {"success": True, "total_tokens": len(DEVICE_TOKENS)}


# 2️⃣ Kirim notifikasi ke semua token
class NotificationInput(BaseModel):
    title: str
    body: str


@app.post("/api/send-notification")
async def send_notification(data: NotificationInput):
    responses = []
    for token in DEVICE_TOKENS:
        res = send_push_notification(token, f"{data.title}\n{data.body}")
        responses.append({"token": token, "response": res})
    return {"success": True, "sent": len(responses), "responses": responses}


# 3️⃣ Analyze text
@app.post("/analyze-text/")
async def analyze_text(input_data: TextInput):
    result = detect_harmful_content(input_data.text)

    if result["flagged"]:
        alert_msg = f"Pesan mencurigakan:\n{result['text']}\n\nDetail: {result['analysis']}"
        if input_data.parent_email:
            send_email_alert(input_data.parent_email, alert_msg)
        if input_data.parent_token:
            send_push_notification(input_data.parent_token, alert_msg)

    return result


# 4️⃣ Analyze image
@app.post("/analyze-image/")
async def analyze_image(file: UploadFile=File(...), parent_email: str=Form(None), parent_token: str=Form(None)):
    text = extract_text_from_image(file.file)
    result = detect_harmful_content(text)

    if result["flagged"]:
        alert_msg = f"Pesan mencurigakan (dari gambar):\n{text}\n\nDetail: {result['analysis']}"
        if parent_email:
            send_email_alert(parent_email, alert_msg)
        if parent_token:
            send_push_notification(parent_token, alert_msg)

    return {"text": text, **result}
