from transformers import pipeline
import re

classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    top_k=None,
    framework="pt"
)

HARMFUL_KEYWORDS = [
    # Cyber/umum
    "cyber bullying", "pelecehan", "sara", "diskriminasi", "intimidasi",
    "narkoba", "drugs", "seksual", "pornografi", "kekerasan", "bully", "racist",
    
    # Kasar / penghinaan umum
    "bodoh", "anjing", "kampret", "tai", "brengsek", "monyet", "goblok", "asu",
    "bajingan", "sampah", "tolol", "idiot", "gila", "brengsek", "bego", "brengsek", "Bangsat",
    
    # Menyesatkan / merendahkan
    "busuk", "hina", "sialan", "cabul", "penipu", "pembohong", "brengsek", "tolol",
    "goblok", "brengsek", "bodoh amat", "gila kau", "brengsek kamu",
    
    # Pelecehan seksual
    "haram", "mesum", "seks", "porno", "pelacur", "gila seks", "brengsek seks",
    
    # Slang tambahan
    "asu", "anjing banget", "tai babi", "brengsek banget", "bajingan banget", "goblok banget"
]


def detect_harmful_content(text: str) -> dict:
    # Keyword matching lokal
    flagged_keyword = any(re.search(rf'\b{re.escape(kw)}\b', text, re.IGNORECASE) for kw in HARMFUL_KEYWORDS)
    
    # Analisis model
    nlp_results = classifier(text)
    flagged_model = any(
        score["score"] > 0.05
        for score in nlp_results[0]
        if score["label"].lower() in ["toxic", "severe_toxic", "obscene", "insult", "identity_hate"]
    )
    
    flagged = flagged_keyword or flagged_model

    return {
        "text": text,
        "flagged": flagged,
        "analysis": nlp_results
    }
