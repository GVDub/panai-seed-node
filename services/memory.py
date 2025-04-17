

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid
import logging

# Initialize Qdrant client and embedding model
client = QdrantClient(host="localhost", port=6333)
embedder = SentenceTransformer("BAAI/bge-small-en-v1")

# Ensure the collection exists
COLLECTION_NAME = "panai_memory"
VECTOR_SIZE = 384

try:
    client.get_collection(COLLECTION_NAME)
except Exception:
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )

def log_memory_entry(session_id: str, text: str, tags: list = None):
    if tags is None:
        tags = []

    vector = embedder.encode(text).tolist()
    payload = {
        "session_id": session_id,
        "text": text,
        "timestamp": datetime.utcnow().isoformat(),
        "tags": tags
    }
    point = PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload)

    client.upsert(collection_name=COLLECTION_NAME, points=[point])
    logging.info(f"Memory logged for session: {session_id}, tags: {tags}")

def fetch_memories_by_tag(session_id: str, tag: str, limit: int = 10):
    scroll_filter = Filter(
        must=[
            FieldCondition(key="session_id", match=MatchValue(value=session_id)),
            FieldCondition(key="tags", match=MatchValue(value=tag))
        ]
    )
    result, _ = client.scroll(collection_name=COLLECTION_NAME, scroll_filter=scroll_filter, limit=limit)
    return [point.payload["text"] for point in result]