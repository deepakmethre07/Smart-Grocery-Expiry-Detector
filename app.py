# app.py
import streamlit as st
from PIL import Image
from datetime import datetime
import os
from dotenv import load_dotenv

import ocr_utils
import db

load_dotenv()

st.set_page_config(page_title='Smart Grocery Expiry Detector', layout='centered')
st.title("🛒 Smart Grocery Expiry Detector")

# Initialize DB
db.init_db()

uploaded = st.file_uploader("Upload a photo of the product/package", type=['png','jpg','jpeg'])
use_easyocr = st.checkbox("Use EasyOCR (alternative to Tesseract)", value=False)

if uploaded:
    try:
        image = Image.open(uploaded)
    except Exception as e:
        st.error(f"Cannot open image: {e}")
        image = None

    if image:
        st.image(image, caption='Uploaded Image', use_column_width=True)

        if st.button("Extract info"):
            with st.spinner("Running OCR..."):
                raw_text = ocr_utils.ocr_image(image, use_easyocr=use_easyocr)
                dates = ocr_utils.extract_dates_from_text(raw_text)
                name = ocr_utils.extract_product_name(raw_text)

            st.subheader("Detected product")
            st.write("**Name:**", name)
            st.write("**Raw OCR text:**")
            st.code(raw_text[:1500] + ("..." if len(raw_text) > 1500 else ""))

            if dates:
                st.success(f"Found {len(dates)} date(s). Using the first parsed date by default.")
                selected = dates[0]
                st.write("**Parsed expiry date:**", selected['date'])
                if st.button("Save item"):
                    db.add_item(name, raw_text, selected['date'])
                    st.balloons()
                    st.success("Saved!")
            else:
                st.warning("No clear date found. Try a clearer photo or different angle.")
                txt = st.text_input("Enter expiry date manually (e.g., 2025-12-10)")
                if st.button("Save manual date") and txt:
                    try:
                        parsed = ocr_utils.try_parse_date_input(txt)
                        if parsed:
                            iso = parsed.isoformat()
                            db.add_item(name, raw_text, iso)
                            st.success("Saved manual date.")
                        else:
                            st.error("Couldn't parse the date. Use YYYY-MM-DD or a clear date format.")
                    except Exception as e:
                        st.error(f"Error saving manual date: {e}")

st.subheader("Saved items")
rows = db.list_items()
if rows:
    import pandas as pd
    df = []
    for r in rows:
        id_, name, expiry, added = r
        try:
            days_left = (datetime.fromisoformat(expiry) - datetime.now()).days if expiry else None
        except Exception:
            days_left = None
        df.append((id_, name, expiry, days_left))
    df = pd.DataFrame(df, columns=['id','name','expiry_date','days_left'])
    st.dataframe(df)
else:
    st.write("No items yet. Upload an image to start.")

# Optional: small instructions
st.markdown("---")
st.info("Tip: For best OCR, crop tightly to the label, ensure good lighting, and avoid glare.")
