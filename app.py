
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import random

st.set_page_config(page_title="Quiz Image Generator", layout="centered")
st.title("🔤 Fill-the-Blank Image Generator (Dark Blue with Padding)")
st.markdown("Upload your Excel file to generate images showing one random letter and blanks.")

uploaded_file = st.file_uploader("Upload your .xlsx quiz file", type=["xlsx"])

FONT_PATH = "fonts/Montserrat.ttf"
BG_PATH = "background.jpg"
TEXT_COLOR = "#002C6A"
PADDING = 40  # padding from edges

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df = df.iloc[:, 1]  # Column B: Correct Answer
        df = df.fillna('').astype(str)

        bg = Image.open(BG_PATH).convert("RGB")
        image_size = bg.size
        font = ImageFont.truetype(FONT_PATH, 72)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, answer in enumerate(df):
                word = answer.lower().strip()
                if not word:
                    continue

                reveal_index = random.randint(0, len(word)-1)
                masked = [char if i == reveal_index else '_' for i, char in enumerate(word)]
                display_text = ' '.join(masked)

                img = bg.copy()
                draw = ImageDraw.Draw(img)

                bbox = draw.textbbox((0, 0), display_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = max((image_size[0] - text_width) // 2, PADDING)
                y = max((image_size[1] - text_height) // 2, PADDING)

                draw.text((x, y), display_text, font=font, fill=TEXT_COLOR)

                filename = f"q{idx+1:02d}_{word}.png"
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                zip_file.writestr(filename, img_bytes.read())

        zip_buffer.seek(0)
        st.success("✅ Images generated!")
        st.download_button("Download ZIP", zip_buffer, file_name="quiz_images.zip", mime="application/zip")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
