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

# Path model kamu
MODEL_PATH = "./kiddygo_model_v2"

# Mapping label index → nama label
LABELS = {
    0: "normal",
    1: "hate_toxic",
    2: "abusive_insult"
}

# Load tokenizer + model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# Pipeline dengan return_all_scores=True supaya kita dapat semua probabilitas label
classifier = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    top_k=None,   # penting
    framework="pt"
)


def classify_text(text: str) -> Dict:
    """
    Mengklasifikasikan satu teks menjadi salah satu label [normal, hate_toxic, abusive_insult]
    dan mengembalikan skor semua label.
    """
    results = classifier(text)[0]  # list of dict [{'label': 'LABEL_0', 'score': ...}, ...]
    
    # Konversi label 'LABEL_0' ke nama label kamu
    scores = []
    for r in results:
        idx = int(r["label"].replace("LABEL_", ""))  # ambil index label
        scores.append({
            "label": LABELS[idx],
            "score": float(r["score"])
        })

    # Ambil label dengan score tertinggi
    best = max(scores, key=lambda x: x["score"])

    return {
        "text": text,
        "predicted_label": best["label"],
        "score": best["score"],
        "all_scores": scores
    }


def detect_harmful_content(text: str, threshold: float = 0.5) -> Dict:
    """
    Mengecek apakah teks termasuk kategori harmful (hate_toxic atau abusive_insult)
    dengan threshold probabilitas tertentu.
    """
    result = classify_text(text)
    harmful = (
        result["predicted_label"] in ["hate_toxic", "abusive_insult"]
        and result["score"] >= threshold
    )

    result["flagged"] = harmful
    result["analysis"] = "Konten berbahaya terdeteksi" if harmful else "Konten normal / aman"
    return result