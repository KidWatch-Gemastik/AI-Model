import easyocr

reader = easyocr.Reader(['en', 'id'])  # Bahasa Indonesia + Inggris

def extract_text_from_image(image_path):
    results = reader.readtext(image_path, detail=0)
    text = " ".join(results)
    return text
