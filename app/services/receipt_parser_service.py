import json

import pytesseract

from PIL import Image
from PIL import ImageEnhance

from google import genai

import os
import uuid
from dotenv import load_dotenv

from werkzeug.utils import secure_filename
from flask import current_app

load_dotenv()

class ReceiptParserService:

    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

    client = genai.Client(
        api_key=GEMINI_API_KEY
        
    )

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    @staticmethod
    def save_image(image):

        if image is None:
            raise ValueError("No image uploaded.")

        filename = secure_filename(image.filename)

        if filename == "":
            raise ValueError("Invalid filename.")

        extension = filename.rsplit(".", 1)[-1].lower()

        if extension not in ReceiptParserService.ALLOWED_EXTENSIONS:
            raise ValueError("Unsupported image format.")

        filename = (
            f"{uuid.uuid4().hex}.{extension}"
        )

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "uploads",
            "receipts"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        image_path = os.path.join(
            upload_folder,
            filename
        )

        image.save(image_path)

        return image_path


    @staticmethod
    def extract_text(image_path):

        image = Image.open(image_path).convert("L")

        enhancer = ImageEnhance.Contrast(image)

        image = enhancer.enhance(2)

        text = pytesseract.image_to_string(
            image,
            config="--oem 3 --psm 6"
        )

        return text


    @staticmethod
    def parse_receipt(raw_text):

        prompt = f"""
Extract the following information from this receipt text and return it as JSON.

{{
    "vendor_name": <string: vendor or shop name>,
    "items": {{
        <string: item name>: <float: item cost>
    }},
    "taxes": {{
        <string: tax name>: <float: tax amount>
    }},
    "discounts": {{
        <string: discount name>: <float: discount amount>
    }},
    "total": <float: total amount>
}}

Rules:
- Return ONLY valid JSON.
- No markdown.
- No explanation.
- Item prices should be numbers.
- Taxes and discounts should be dictionaries.
- If taxes or discounts are absent, return empty dictionaries.

Receipt Text:

{raw_text}
"""

        response = ReceiptParserService.client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        text = response.text.strip()

        if text.startswith("```json"):

            text = (
                text.replace("```json", "")
                    .replace("```", "")
                    .strip()
            )

        return json.loads(text)


    @staticmethod
    def get_data(image_path):

        raw_text = ReceiptParserService.extract_text(
            image_path
        )

        data = ReceiptParserService.parse_receipt(
            raw_text
        )

        print(type(data))

        return data