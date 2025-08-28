# Whitespace cleanup and text normalization.
import re
import typing

def normalize_whitespace(text: str) -> str:
   
    text = re.sub(r'\r\n?', '\n', text)
    
   
    text = re.sub(r'\n{3,}', '\n\n', text)
    

    text = re.sub(r' {2,}', ' ', text)
    
   
    text = text.strip()
    
    return text

def clean_text(text: str) -> str:
    text = normalize_whitespace(text)
    text = re.sub(r'\u00AD', '\u200B-\u200d\uFEFF', text)
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    return text
