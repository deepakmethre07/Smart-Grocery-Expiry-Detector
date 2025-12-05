![Smart Grocery Expiry Detector](assets/banner.png)
# Smart Grocery Expiry Detector


A beginner-friendly project that extracts product names and expiry dates from photos of packaged groceries. Built with Python, OCR (Tesseract/EasyOCR), OpenCV, and Streamlit. Includes a simple SQLite database and an optional email reminder worker.


## Features (MVP)
- Upload product image via Streamlit UI
- Preprocess image for OCR
- Extract text (Tesseract or EasyOCR)
- Parse and normalize expiry dates
- Save items to SQLite
- View saved items with days-to-expiry
- Optional daily email reminders for items expiring soon


## Tech stack
- Python
- Streamlit (UI)
- pytesseract or EasyOCR (OCR)
- OpenCV (image preprocessing)
- dateparser (date parsing)
- SQLite (database)
- APScheduler + smtplib (reminders)


## Quick start
1. Install Tesseract (if using pytesseract):
- Windows: install from the official Tesseract installer and add to PATH.
- Linux (Debian/Ubuntu): `sudo apt-get install tesseract-ocr`
- macOS (Homebrew): `brew install tesseract`


2. Create virtual environment and install Python packages:


```bash
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt
