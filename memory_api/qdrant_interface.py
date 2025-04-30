"""Qdrant database interface and helper functions."""

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

client = QdrantClient(
    host="localhost",
    port=6333,
    prefer_grpc=False,
)

__all__ = ["client", "ensure_panai_memory_collection", "get_qdrant_client"]

def get_qdrant_client(host="qdrant", port=6333):
    return QdrantClient(host=host, port=port)

def ensure_panai_memory_collection(client=None):
    if client is None:
        client = get_qdrant_client()
    collections = client.get_collections().collections
    if not any(col.name == "panai_memory" for col in collections):
        print("[PanAI] Creating missing 'panai_memory' collection...")
        client.create_collection(
            collection_name="panai_memory",
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
    else:
        print("[PanAI] Collection 'panai_memory' already exists.")