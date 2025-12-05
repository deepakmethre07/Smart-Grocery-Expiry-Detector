# ocr_utils.py
import re
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import pytesseract
import dateparser

# If using Windows and Tesseract not in PATH, uncomment and edit the line below:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image_pil(pil_image):
    """
    Basic preprocessing using PIL image -> OpenCV.
    Returns a thresholded grayscale image (numpy array) suitable for pytesseract.
    """
    img = np.array(pil_image.convert('RGB'))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Resize for better OCR (scale down if very large)
    h, w = gray.shape
    scale = 1000 / max(h, w)
    if scale < 1:
        gray = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    # Denoise and threshold
    blur = cv2.bilateralFilter(gray, 9, 75, 75)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th


def ocr_image(pil_image, use_easyocr=False):
    """
    Return raw OCR text from a PIL image.
    If use_easyocr is True, uses easyocr; otherwise uses pytesseract.
    """
    if use_easyocr:
        import easyocr
        reader = easyocr.Reader(['en'])
        img = np.array(pil_image.convert('RGB'))
        results = reader.readtext(img)
        text = '\n'.join([r[1] for r in results])
        return text
    else:
        img = preprocess_image_pil(pil_image)
        # config to improve date & numbers recognition
        config = r'--psm 6'
        text = pytesseract.image_to_string(img, config=config)
        return text


DATE_REGEXES = [
    # DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
    r'(\d{1,2}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{2,4})',
    # YYYY-MM-DD
    r'(\d{4}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{1,2})',
    # Month DD, YYYY  (e.g., December 10, 2025)
    r'([A-Za-z]{3,9}\s+\d{1,2},?\s*\d{4})',
    # DD Month YYYY (e.g., 10 December 2025)
    r'(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})',
    # EXP: DD/MM/YYYY or similar
    r'(EXP[:\s]*\d{1,2}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{2,4})',
    # Best before / Best before: text
    r'(Best before[:\s]*[A-Za-z0-9\-/ ]+)',
]


def extract_dates_from_text(text):
    """
    Attempt to find and parse date-like substrings, then return normalized dates.
    Returns a list of dicts: [{'raw': <matched_text>, 'date': 'YYYY-MM-DD'}, ...]
    """
    candidates = []

    # Find regex matches
    for reg in DATE_REGEXES:
        for m in re.findall(reg, text, flags=re.I):
            candidates.append(m)

    # fallback: extract tokens that look like numeric dates (additional catch)
    fallback = re.findall(r'(\d{1,2}[\-\/\.]\d{1,2}[\-\/\.]\d{2,4})', text)
    for f in fallback:
        candidates.append(f)

    # Deduplicate while preserving order
    parsed = []
    for c in list(dict.fromkeys(candidates)):
        s = c.strip()
        # Remove common leading labels
        s = re.sub(r'^(exp|best before|expiry|bb|use by)[:\s\-\.]*', '', s, flags=re.I)
        # Try to parse the date, prefer future (useful for expiry dates)
        dt = dateparser.parse(s, settings={'PREFER_DATES_FROM': 'future', 'RELATIVE_BASE': datetime.now()})
        if dt:
            parsed.append({'raw': c, 'date': dt.date().isoformat()})
    return parsed


def extract_product_name(text):
    """
    Simple heuristic to extract a likely product name from OCR text:
    - Take the first few non-empty lines
    - Ignore lines that look like weights, dates, or numeric-only
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for ln in lines[:8]:
        # ignore lines that are digits-only or mostly digits
        if re.search(r'\d', ln) and len(re.findall(r'[A-Za-z]', ln)) < 2:
            continue
        # ignore weight/volume lines
        if re.search(r'\b(g|kg|ml|l|mg)\b', ln.lower()):
            continue
        # pick short-ish lines that could be a product title
        if len(ln) > 2 and len(ln.split()) < 7:
            return ln
    return lines[0] if lines else 'Unknown Product'


def try_parse_date_input(txt):
    """
    Helper for parsing user-entered date strings (returns datetime.date or None).
    Accepts many human-readable formats via dateparser.
    """
    dt = dateparser.parse(txt, settings={'PREFER_DATES_FROM': 'future'})
    return dt.date() if dt else None
