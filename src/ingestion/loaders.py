# PDF (page-first) + DOCX loaders; OCR fallback
import os
from typing import List, Dict, Any
from pypdf import PdfReader
import docx2txt
from .normalize import clean_text
from .ocr import ocr_pdf_page
from src.settings import get_settings

def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    reader = PdfReader(file_path)
    settings = get_settings()
    for page_index in range(len(reader.pages)):
        text = page.extract_text()
        if text is None or len(text.strip()) < 20:
            print(f"Page {page_index + 1}: Using OCR (not enough direct text)")
            text = ocr_pdf_page(file_path, page_index)
        else:
            print(f"Page {page_index + 1}: Using direct text extraction")
        text = clean_text(text or "")
        base_meta = {
            "source": os.path.abspath(file_path),
            "source name": os.path.basename(file_path),
            "ext": "pdf",
            "page start": page_index + 1,
            "page_end": page_index + 1
            }
        page_data = {
            "text": text,
            "meta": base_meta
            }

        pages.append(page_data)
    return pages

def load_docx(file_path: str) -> List[Dict[str, Any]]:
    text = docx2txt.process(file_path) or ""
    text = clean_text(text or "")
    base_meta = {
        "source": os.path.abspath(file_path),
        "source name": os.path.basename(file_path),
        "ext": "docx",
        "page start": 1,
        "page_end": 1
    }
    return [{
        "text": text,
        "meta": base_meta
    }]

def load_any(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    extension = os.path.splitext(file_path.lower())
    if extension == ".pdf":
        return load_pdf(file_path)
    elif extension == ".docx":
        return load_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")