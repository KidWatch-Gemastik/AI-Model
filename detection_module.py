from transformers import pipeline

# Load pre-trained model (public, no token needed)
classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    return_all_scores=True,
    framework="pt"   
)

HARMFUL_KEYWORDS = ["cyber bullying", "pelecehan", "sara", "diskriminasi"]


def detect_harmful_content(text: str):
    flagged_keyword = any(kw.lower() in text.lower() for kw in HARMFUL_KEYWORDS)
    
    nlp_results = classifier(text)
    
    # Turunkan threshold agar lebih sensitif
    flagged_model = any(
        score["score"] > 0.05  # dari 0.5 ke 0.05
        for score in nlp_results[0]
        if score["label"].lower() in ["toxic", "severe_toxic", "obscene", "insult", "identity_hate"]
    )
    
    return flagged_keyword or flagged_model, nlp_results

