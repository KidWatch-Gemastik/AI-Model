from ocr_module import extract_text_from_image
from detection_module import detect_harmful_content


def analyze_notification(input_data, is_image=False):
    if is_image:
        text = extract_text_from_image(input_data)
    else:
        text = input_data
    
    flagged, analysis = detect_harmful_content(text)
    
    return {
        "text": text,
        "flagged": flagged,
        "analysis": analysis
    }
