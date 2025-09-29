# from transformers import pipeline
# import re
# from typing import List, Dict

# # ==============================
# # CONFIGURATION
# # ==============================
# HARMFUL_KEYWORDS: List[str] = [
#     # Cyber/umum
#     "cyber bullying", "pelecehan", "sara", "diskriminasi", "intimidasi",
#     "narkoba", "drugs", "seksual", "pornografi", "kekerasan", "bully", "racist",
#     # Kasar / penghinaan umum
#     "bodoh", "anjing", "kampret", "tai", "brengsek", "monyet", "goblok", "asu",
#     "bajingan", "sampah", "tolol", "idiot", "gila", "bego", "bangsat",
#     # Menyesatkan / merendahkan
#     "busuk", "hina", "sialan", "cabul", "penipu", "pembohong", "bodoh amat",
#     "gila kau", "brengsek kamu",
#     # Pelecehan seksual
#     "haram", "mesum", "seks", "porno", "pelacur", "gila seks",
#     # Slang tambahan
#     "asu", "anjing banget", "tai babi", "brengsek banget", "bajingan banget", "goblok banget"
# ]

# # Model names
# MODEL_EN = "unitary/toxic-bert"  # English
# MODEL_ID = "indobenchmark/indobert-base-p1"  # Bahasa Indonesia, bisa diganti fine-tuned toxic

# # Thresholds
# THRESHOLD = 0.05
# TOXIC_LABELS = ["toxic", "severe_toxic", "obscene", "insult", "identity_hate"]

# # ==============================
# # MODEL INITIALIZATION
# # ==============================
# def get_classifier(model_name: str):
#     """Initialize HuggingFace pipeline."""
#     return pipeline("text-classification", model=model_name, top_k=None, framework="pt")

# classifier_en = get_classifier(MODEL_EN)
# classifier_id = pipeline("text-classification", model=MODEL_ID, top_k=None, framework="pt")

# # ==============================
# # HELPER FUNCTIONS
# # ==============================
# def contains_harmful_keyword(text: str, keywords: List[str]) -> bool:
#     return any(re.search(rf'\b{re.escape(kw)}\b', text, re.IGNORECASE) for kw in keywords)

# def model_flags_text(text: str, classifier) -> float:
#     """Return toxic score from a model."""
#     results = classifier(text)
#     scores = results[0] if isinstance(results[0], list) else results
#     toxic_score = sum(score["score"] for score in scores if score["label"].lower() in TOXIC_LABELS)
#     return toxic_score

# # ==============================
# # MAIN FUNCTION
# # ==============================
# def detect_harmful_content(text: str) -> Dict:
#     keyword_flagged = contains_harmful_keyword(text, HARMFUL_KEYWORDS)
    
#     score_en = model_flags_text(text, classifier_en)
#     score_id = model_flags_text(text, classifier_id)
    
#     combined_score = max(score_en, score_id)
#     model_flagged = combined_score > THRESHOLD
#     flagged = keyword_flagged or model_flagged
    
#     # Buat ringkasan analysis
#     analysis = []
#     if keyword_flagged:
#         analysis.append("Terdapat kata kunci berbahaya")
#     if model_flagged:
#         analysis.append("Model mendeteksi konten berbahaya")
    
#     return {
#         "text": text,
#         "flagged": flagged,
#         "keyword_flagged": keyword_flagged,
#         "model_flagged": model_flagged,
#         "score_en": score_en,
#         "score_id": score_id,
#         "combined_score": combined_score,
#         "analysis": "; ".join(analysis) if analysis else "Tidak ada indikasi bahaya"
#     }

# from transformers import pipeline
# from typing import Dict

# # ==============================
# # CONFIGURATION
# # ==============================

# # Ganti dengan path lokal atau nama repo HuggingFace
# MODEL_EN = "unitary/toxic-bert"        # optional untuk teks English
# MODEL_ID = "./my_model"                # contoh: path lokal
# # MODEL_ID = "username/nama-model-toxic"  # kalau sudah upload ke HuggingFace Hub

# # Threshold untuk menentukan apakah teks dianggap toxic
# THRESHOLD = 0.05
# TOXIC_LABELS = ["toxic", "severe_toxic", "obscene", "insult", "identity_hate"]

# # ==============================
# # MODEL INITIALIZATION
# # ==============================
# def get_classifier(model_name: str):
#     """Initialize HuggingFace pipeline."""
#     return pipeline("text-classification", model=model_name, top_k=None, framework="pt")

# classifier_en = get_classifier(MODEL_EN)
# classifier_id = get_classifier(MODEL_ID)

# # ==============================
# # HELPER FUNCTION
# # ==============================
# def model_flags_text(text: str, classifier) -> float:
#     """Return toxic score from a model."""
#     results = classifier(text)
#     scores = results[0] if isinstance(results[0], list) else results
#     toxic_score = sum(score["score"] for score in scores if score["label"].lower() in TOXIC_LABELS)
#     return toxic_score

# # ==============================
# # MAIN FUNCTION
# # ==============================
# def detect_harmful_content(text: str) -> Dict:
#     score_en = model_flags_text(text, classifier_en)
#     score_id = model_flags_text(text, classifier_id)

#     combined_score = max(score_en, score_id)
#     model_flagged = combined_score > THRESHOLD

#     return {
#         "text": text,
#         "flagged": model_flagged,
#         "score_en": score_en,
#         "score_id": score_id,
#         "combined_score": combined_score,
#         "analysis": "Model mendeteksi konten berbahaya" if model_flagged else "Tidak ada indikasi bahaya"
#     }

# ==============================
# TEST
# ==============================
# if __name__ == "__main__":
#     test_text = "anjing kamu goblok banget"
#     result = detect_harmful_content(test_text)
#     print(result)

# ==============================
# CONFIGURATION
# ==============================
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from typing import Dict

MODEL_PATH = "./toxic-detector-v2"
THRESHOLD = 0.05
TOXIC_LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

# Load tokenizer + model manual
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# Pipeline dengan tokenizer & model yang sudah benar
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None, framework="pt")


def model_flags_text(text: str) -> float:
    results = classifier(text)
    scores = results[0] if isinstance(results[0], list) else results
    toxic_score = sum(score["score"] for score in scores if score["label"].lower() in TOXIC_LABELS)
    return toxic_score


def detect_harmful_content(text: str) -> Dict:
    results = classifier(text, top_k=None)
    scores = results[0] if isinstance(results[0], list) else results

    # ambil label dengan skor tertinggi
    best = max(scores, key=lambda x: x["score"])
    flagged = best["label"].lower() in TOXIC_LABELS and best["score"] > 0.5

    return {
        "text": text,
        "flagged": flagged,
        "predicted_label": best["label"],
        "score": best["score"],
        "analysis": "Model mendeteksi konten berbahaya" if flagged else "Tidak ada indikasi bahaya"
    }

