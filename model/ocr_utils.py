
import cv2
import pytesseract
from PIL import Image
import numpy as np
from typing import List

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_for_ocr(image_path: str):
    
    try:
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if img is None:
            raise Exception(f"Failed to read image: {image_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Otsu thresholding
        _, binary = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Light denoising for OCR
        denoised = cv2.fastNlMeansDenoising(binary, h=15)

        return denoised

    except Exception as e:
        raise Exception(f"Error during OCR preprocessing: {e}")


def ocr_image_text_lines(image_path: str) -> List[str]:
    
    processed = preprocess_for_ocr(image_path)

    # Convert to PIL format
    pil_img = Image.fromarray(processed)

    # OCR config tuned for tabular text
    config = "--oem 3 --psm 6"

    try:
        text = pytesseract.image_to_string(pil_img, config=config)
    except Exception as e:
        raise Exception(f"OCR failed: {e}")

    # Split into lines & remove empty ones
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return lines
