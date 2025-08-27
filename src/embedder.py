# Embedding wrapper for BAAI/bge-m3.
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import torch
import os
from .settings import get_settings

_MODEL_ = None
def get_model():
    global _MODEL_
    if _MODEL_ is None:
        settings = get_settings()
        _MODEL_ = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Move to GPU if CUDA is available
        if torch.cuda.is_available():
            _MODEL_ = _MODEL_.to('cuda')
            
    return _MODEL_

class EmbeddingService:
    def __init__(self):
        self.model = get_model()

    def encode_texts(self, testx: List[str]) -> np.ndarray:
        return self.model.encode(
            testx, 
            batch_size=32,
            normalize_embeddings=True, 
            convert_to_numpy=True, 
            show_progress_bar=True
        )
