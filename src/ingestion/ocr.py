# Tesseract-based OCR for scanned PDF pages.
from pytesseract import pytesseract
from PIL import Image
import fitz
from typing import IO
from src.settings import get_settings

def tesseract_langs_from_hints(hints: str) -> str:
   
    language_map = {
        "en": "eng",  
        "pl": "pol",  
    }
    
    
    if not hints or not hints.strip():
        return "eng"  
    
    
    lang_codes = hints.split(",")
    
    
    tesseract_codes = []
    for code in lang_codes:
        
        clean_code = code.strip().lower()
        
        
        if clean_code in language_map:
            tesseract_code = language_map[clean_code]
           
            if tesseract_code not in tesseract_codes:
                tesseract_codes.append(tesseract_code)
    
    
    if tesseract_codes:
        return "+".join(tesseract_codes)  
    else:
        return "eng"    
    
def ocr_pdf_page(file_path: str, page_index: int, dpi: int=300) -> str:

    settings = get_settings()
    

    doc = fitz.open(file_path)
    page = doc.load_page(page_index)
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
    mode = "RGBA" if pix.alpha else "RGB"
    img = PIL.Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    langs = tesseract_langs_from_hints(get_settings().LANGUAGE_HINTS)
    text = pytesseract.image_to_string(img, lang=langs)
    text = text.strip()
    return text 