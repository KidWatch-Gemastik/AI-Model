from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

# 1. Load kembali tokenizer & model hasil training
model_path = "./kiddygo_model_v2" 
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

model.eval()  # set ke evaluasi

# 2. Fungsi prediksi tunggal
def predict_text(text: str):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128
    )
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        pred_id = torch.argmax(logits, dim=1).item()
        probs = torch.nn.functional.softmax(logits, dim=1).cpu().numpy()[0]
    return pred_id, probs

# 3. Label mapping biar mudah dibaca
label_map = {
    0: "Normal",
    1: "Hate Speech/Toxicity",
    2: "Abusive/Profanity/Insults"
}

# 4. Contoh test beberapa kalimat
test_texts = [
    "Kamu kotoran binatang",    # abusive
    "Mari kita makan bersama",  # normal
    "Saya akan menyerang kamu!",  # hate speech/toxicity
]

for t in test_texts:
    pred_id, probs = predict_text(t)
    print(f"Teks: {t}")
    print(f"Prediksi: {pred_id} - {label_map[pred_id]} (prob: {probs})\n")
