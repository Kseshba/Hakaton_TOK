import pdfplumber
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import os

# Установите путь к Tesseract (уже установленный в коде)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Функция для обработки PDF
def extract_text_from_pdf(pdf_path):
    full_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                # Применяем OCR если встроенный текст отсутствует
                pil_image = page.to_image().original
                text = pytesseract.image_to_string(pil_image, lang='rus')

            full_text += text + "\n"

    return full_text
