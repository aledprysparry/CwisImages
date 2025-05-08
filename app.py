
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import random
import re

st.set_page_config(page_title="Welsh Digraph Quiz Image Generator", layout="centered")
st.title("🟡 Cwis Bob Dydd: Image Generator with Welsh Digraphs")

uploaded_file = st.file_uploader("Upload your .xlsx quiz file", type=["xlsx"])

FONT_PATH = "fonts/Montserrat.ttf"
BG_PATH = "background.jpg"
TEXT_COLOR = "#002C6A"
IMAGE_SIZE = 540
PADDING = 40
MAX_TEXT_WIDTH = IMAGE_SIZE - 2 * PADDING

# Welsh digraphs
WELSH_DIGRAPHS = ["ch", "dd", "ff", "ng", "ll", "ph", "rh", "th"]

def split_welsh_letters(word):
    word = word.lower()
    letters = []
    i = 0
    while i < len(word):
        if i + 1 < len(word) and word[i:i+2] in WELSH_DIGRAPHS:
            letters.append(word[i:i+2])
            i += 2
        else:
            letters.append(word[i])
            i += 1
    return letters

def create_text_image(text, font, bg_img, text_color):
    img = bg_img.copy()
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = max((IMAGE_SIZE - text_width) // 2, PADDING)
    y = max((IMAGE_SIZE - text_height) // 2, PADDING)
    draw.text((x, y), text, font=font, fill=text_color)
    return img

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df = df.iloc[:, 1]  # Correct answers only
        df = df.fillna('').astype(str)

        bg = Image.open(BG_PATH).convert("RGB")
        font = ImageFont.truetype(FONT_PATH, 72)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, answer in enumerate(df):
                word = answer.strip().lower()
                if not word:
                    continue

                letters = split_welsh_letters(word)
                if not letters:
                    continue

                reveal_index = random.randint(0, len(letters) - 1)
                masked_letters = [l if i == reveal_index else "_" for i, l in enumerate(letters)]
                display_text = " ".join(masked_letters)
                correct_text = " ".join(letters)

                masked_img = create_text_image(display_text, font, bg, TEXT_COLOR)
                correct_img = create_text_image(correct_text, font, bg, TEXT_COLOR)

                base_name = f"q{idx+1:02d}_{word.replace(' ', '_')}"
                
                for suffix, image in [("", masked_img), ("_correct", correct_img)]:
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    zip_file.writestr(f"{base_name}{suffix}.png", img_bytes.read())

        zip_buffer.seek(0)
        st.success("✅ Images generated!")
        st.download_button("Download All Images (.zip)", zip_buffer, file_name="quiz_images.zip", mime="application/zip")

    except Exception as e:
        st.error(f"❌ Error: {e}")
