# main.py
from fastapi import FastAPI, UploadFile, File, Form
from analyzer import analyze_notification

app = FastAPI(title="Notification Safety Detector")


@app.post("/analyze-text/")
async def analyze_text(text: str=Form(...)):
    result = analyze_notification(text, is_image=False)
    return result


@app.post("/analyze-image/")
async def analyze_image(file: UploadFile=File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    result = analyze_notification(file_path, is_image=True)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
