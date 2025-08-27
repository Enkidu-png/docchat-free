# Token-aware text splitter (~800 tokens, 120 overlap).
import tiktoken

from typing import List, Dict, Any, Optional

from .settings import get_settings

import math

_ENCODING = None

def _get_encoding():
    """Get cached encoding, load once if needed."""
    global _ENCODING
    if _ENCODING is None:
        _ENCODING = tiktoken.get_encoding("cl100k_base")
    return _ENCODING

def count_tokens(text: str) -> int:
    """Count tokens in text."""
    encoding = _get_encoding()
    return len(encoding.encode(text))

def slice_by_tokens(text: str, start_tok: int, end_tok: int) -> str:
    """Slice text by token positions and decode back to text."""
    encoding = _get_encoding()
    tokens = encoding.encode(text)
    return encoding.decode(tokens[start_tok:end_tok])





class TokenAwareSplitter:
    def __init__(self, chunk_tokens=None, overlap_tokens=None):
        if chunk_tokens is None or overlap_tokens is None:
            settings = get_settings()
            if chunk_tokens is None:
                chunk_tokens = settings.CHUNK_TOKENS  # 800
            if overlap_tokens is None:
                overlap_tokens = settings.CHUNK_OVERLAP  # 120

        # Validate: overlap must be smaller than chunk size
        if overlap_tokens >= chunk_tokens:
            raise ValueError(f"Overlap ({overlap_tokens}) must be smaller than chunk size ({chunk_tokens})")

        # Store configuration
        self.chunk_tokens = chunk_tokens
        self.overlap_tokens = overlap_tokens
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def split_text(self, text: str, base_meta: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Tokenize the whole text once
        tokens = self.encoding.encode(text)

        # Calculate sliding window parameters
        window = self.chunk_tokens
        step = self.chunk_tokens - self.overlap_tokens

        chunks = []
        chunk_id = 0

        # Use sliding window approach
        for i in range(0, len(tokens), step):
            # Get token slice
            token_slice = tokens[i:i + window]

            # Stop if empty
            if not token_slice:
                break

            # Decode back to string and clean whitespace
            chunk_text = self.encoding.decode(token_slice).strip()

            # Create metadata dict
            metadata = {}
            if base_meta:
                metadata.update(base_meta)  # Copy base metadata

            # Add chunk-specific metadata
            metadata.update({
                "chunk_id": chunk_id,
                "token_count": len(token_slice)
            })

            # Append chunk to results
            chunks.append({
                "text": chunk_text,
                "metadata": metadata
            })

            chunk_id += 1

        return chunks