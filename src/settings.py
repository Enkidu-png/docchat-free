from typing import Optional, List
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator, computed_field, validator




class Settings(BaseSettings):
    # Core services
    QDRANT_URL: str
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "docchat"
    
    # LLM and Embeddings  
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    LLM_MODEL: str = "phi3.5"
    
    # Ingestion
    DOC_DIR: str = "./data"
    ALLOWED_EXTS: str = ".pdf, .docx"
    CHUNK_TOKENS: int = 800
    CHUNK_OVERLAP: int = 120
    
    # Retrieval
    TOP_K: int = 5
    MMR: bool = True
    RERANK: bool = True
    MULTI_QUERY: int = 2
    LANGUAGE_HINTS: str = "en, pl"
    OCR_ENABLED: bool = True
    OCR_LANGS: str = "eng,pol"

    # Pydantic configuration
    class Config:
        env_file = "configs/.env"
        env_file_encoding = "utf-8"

    @validator('DOC_DIR')
    def validate_doc_dir(cls, v):
        """Convert to Path and ensure directory exists"""
        doc_path = Path(v)
        
        # Create dir if it doesn't exist
        try:
            doc_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create DOC_DIR '{v}': {e}")
        
        # Return path object
        return doc_path
    
    @computed_field
    @property
    def allowed_extensions(self) -> List[str]:
        """Parse ALLOWED_EXTS into a clean list of extensions"""
        if not self.ALLOWED_EXTS.strip():
            return []
        
        extensions = []
        for ext in self.ALLOWED_EXTS.split(','):
            ext = ext.strip()
            if not ext:
                continue
            
            # Ensure starts with dot (.pdf .docx)
            if not ext.startswith('.'):
                ext = '.' + ext
            
            extensions.append(ext.lower())
        
        if not extensions:
            raise ValueError("ALLOWED_EXTS must contain at least one valid extension")
        
        return extensions
    
    @validator('CHUNK_TOKENS')
    def validate_chunk_tokens(cls, v):
        """Ensure CHUNK_TOKENS is positive"""
        if v <= 0:
            raise ValueError("CHUNK_TOKENS must be greater than 0")
        return v
    
    @validator('CHUNK_OVERLAP')
    def validate_chunk_overlap(cls, v):
        """Ensure CHUNK_OVERLAP is non-negative"""
        if v < 0:
            raise ValueError("CHUNK_OVERLAP must be >= 0")
        return v
    
    @validator('CHUNK_OVERLAP')
    def validate_overlap_vs_tokens(cls, v, values):
        """Ensure CHUNK_OVERLAP is less than CHUNK_TOKENS"""
        chunk_tokens = values.get('CHUNK_TOKENS', 0)
        if v >= chunk_tokens:
            raise ValueError(f"CHUNK_OVERLAP ({v}) must be less than CHUNK_TOKENS ({chunk_tokens})")
        return v
    
    @validator('TOP_K')
    def validate_top_k(cls, v):
        """Ensure TOP_K is at least 1"""
        if v < 1:
            raise ValueError("TOP_K must be >= 1")
        return v
    
    @validator('MULTI_QUERY')
    def validate_multi_query(cls, v):
        """Ensure MULTI_QUERY is non-negative"""
        if v < 0:
            raise ValueError("MULTI_QUERY must be >= 0")
        return v
    
    @computed_field
    @property
    def language_list(self) -> List[str]:
        """Parse LANGUAGE_HINTS into a clean list of language codes"""
        if not self.LANGUAGE_HINTS.strip():
            return []
        
        languages = []
        for lang in self.LANGUAGE_HINTS.split(','):
            lang = lang.strip().lower()
            if lang:
                languages.append(lang)
        
        if not languages:
            raise ValueError("LANGUAGE_HINTS must contain at least one language code")
        
        
        return languages
def get_settings() -> Settings:
    """Get the application settings."""
    return Settings()