
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import random

st.set_page_config(page_title="Quiz Image Generator", layout="centered")
st.title("🔤 Lowercase Fill-the-Blank Image Generator")
st.markdown("Upload your Excel file to generate images that show one random letter and blanks for the rest.")

uploaded_file = st.file_uploader("Upload your .xlsx quiz file", type=["xlsx"])

FONT_PATH = "fonts/Montserrat.ttf"
BG_PATH = "background.jpg"

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df = df.iloc[:, 1]  # Only column B (Correct Answer)
        df = df.fillna('').astype(str)

        bg = Image.open(BG_PATH).convert("RGB")
        image_size = bg.size
        font = ImageFont.truetype(FONT_PATH, 72)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, answer in enumerate(df):
                word = answer.lower()
                if len(word.strip()) == 0:
                    continue

                # Choose a random index to reveal
                reveal_index = random.randint(0, len(word)-1)
                masked = [char if i == reveal_index else '_' for i, char in enumerate(word)]
                display_text = ' '.join(masked)

                img = bg.copy()
                draw = ImageDraw.Draw(img)

                # Get text size and position
                text_width, text_height = draw.textsize(display_text, font=font)
                x = (image_size[0] - text_width) // 2
                y = (image_size[1] - text_height) // 2

                draw.text((x, y), display_text, font=font, fill='black')

                # Save image to zip
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
