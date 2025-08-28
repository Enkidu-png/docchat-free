# Qdrant client + collection init + upsert/query.
from qdrant_client import QdrantClient

from qdrant_client.http.models import Distance, VectorParams, PayloadSchemaType

from typing import List, Dict, Any, Optional

from src.settings import get_settings

from src.embedder import EmbeddingService

import hashlib


__client: Optional[QdrantClient] = None

def get_client() -> QdrantClient:
    """
    Reads QDRANT_URL and QDRANT_API_KEY from settings.
    Creates and caches a QdrantClient instance.
    Returns the same client on subsequent calls.
    """
    global __client
    
    if __client is None:
        settings = get_settings()
        __client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        print("A new QdrantClient instance was created.")
    
    return __client

def ensure_collection(client: QdrantClient, name: str, vector_size: int, on_disk: bool = False) -> None:
 
    if client.collection_exists(collection_name=name):
        print(f"Collection '{name}' already exists. Skipping creation.")
        return
    else:
        print(f"Collection '{name}' not found. Creating a new one...")
        
        vectors_config = VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
            on_disk=on_disk
        )
        
        client.create_collection(
            collection_name=name,
            vectors_config=vectors_config
        )
        print(f"Collection '{name}' created successfully.")

def ensure_payload_indexes(client: QdrantClient, name: str) -> None:
 
    index_fields = ["doc_id", "source_name", "ext", "language"]
    
    # Check if the collection exists before attempting to add indexes.
    if not client.collection_exists(collection_name=name):
        print(f"Collection '{name}' does not exist. Cannot create payload indexes.")
        return
        
    collection_info = client.get_collection(collection_name=name)
    existing_indexes = collection_info.payload_schema.keys()
    
    for field in index_fields:
        if field not in existing_indexes:
            print(f"Index for field '{field}' not found. Creating a new keyword index.")
            
            client.create_payload_index(
                collection_name=name,
                field_name=field,
                field_schema=PayloadSchemaType.KEYWORD
            )
            print(f"Keyword index for '{field}' created successfully.")
        else:
            print(f"Index for field '{field}' already exists. Skipping.")

def build_point_id(doc_id: str, chunk_id: int) -> str:
    
    unique_string = f"{doc_id}:{chunk_id}"
    sha1_hash = hashlib.sha1(unique_string.encode('utf-8'))
    return sha1_hash.hexdigest()

