# Standard library imports
from typing import List
from datetime import datetime
import uuid

#third-party imports
from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

import requests

app = FastAPI()
client = QdrantClient(host="localhost", port=6333)

# Load BGE-small-en model for embedding
embed_model = SentenceTransformer("BAAI/bge-small-en")

def embed_text(text: str) -> list:
    return embed_model.encode(text, normalize_embeddings=True).tolist()

class QueryRequest(BaseModel):
    vector: list
    limit: int = 1

class TextQuery(BaseModel):
    text: str
    limit: int = 1

class TagQuery(BaseModel):
    tag: str
    limit: int = 5
    
class SummaryRequest(BaseModel):
    session_id: str
    limit: int = 20  # number of memories to summarize    

@app.post("/search")
def search_memory(request: QueryRequest):
    results = client.search(
        collection_name="panai_memory",
        query_vector=request.vector,
        limit=request.limit
    )
    return {"results": [r.payload for r in results]}

@app.post("/recall")
def recall_from_text(request: TextQuery):
    embedded_vector = embed_text(request.text)
    results = client.search(
        collection_name="panai_memory",
        query_vector=embedded_vector,
        limit=request.limit
    )
    return {"results": [r.payload for r in results]}


@app.post("/search_by_tag")
def search_by_tag(request: TagQuery):
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "tags", "match": {"value": request.tag}}
            ]
        },
        limit=request.limit
    )
    return {"results": [r.payload for r in results]}

class MemoryLog(BaseModel):
    text: str
    session_id: str = "default"
    tags: List[str] = []

@app.post("/log_memory")
def log_memory(entry: MemoryLog):
    vector = embed_text(entry.text)

    point = {
        "id": str(uuid.uuid4()),
        "vector": vector,
        "payload": {
            "text": entry.text,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": entry.session_id,
            "tags": entry.tags,
        }
    }

    client.upsert(
        collection_name="panai_memory",
        points=[point]
    )

    return {"status": "🧠 Memory logged.", "session_id": entry.session_id}

@app.post("/summarize")
def summarize_session(request: SummaryRequest):
    # Pull matching memories
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": request.session_id}}
            ]
        },
        limit=request.limit
    )

    # Combine memory texts
    memories = [r.payload["text"] for r in results[0]]
    combined_text = "\n".join(memories)

    # Ask Mistral for a summary
    summary = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": f"Summarize the following memories:\n{combined_text}\n\nSummary:",
            "stream": False
        }
    ).json()["response"]

    return {
        "session_id": request.session_id,
        "summary": summary.strip()
    }

class ReflectRequest(BaseModel):
    session_id: str
    limit: int = 20

@app.post("/reflect")
def reflect_on_session(request: ReflectRequest):
    # Pull session memories
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": request.session_id}}
            ]
        },
        limit=request.limit
    )

    # Combine memory texts
    memories = [r.payload["text"] for r in results[0]]
    combined_text = "\n".join(memories)

    # Ask Mistral-Nemo for deeper insight
    reflection = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral-nemo",
            "prompt": (
                f"Here is a series of memory logs from session '{request.session_id}':\n\n"
                f"{combined_text}\n\n"
                "Reflect on these memories. What patterns, concerns, or deeper insights emerge?"
            ),
            "stream": False
        }
    ).json()["response"]

    # Log the reflection as a memory
    reflection_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(reflection),
        "payload": {
            "text": reflection,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": request.session_id,
            "tags": ["reflection", "meta"]
        }
    }

    client.upsert(
        collection_name="panai_memory",
        points=[reflection_point]
    )

    return {
        "session_id": request.session_id,
        "reflection": reflection.strip()
    }

class AdviceRequest(BaseModel):
    session_id: str
    limit: int = 10

@app.post("/advice")
def give_advice(request: AdviceRequest):
    # Pull recent reflections
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": request.session_id}},
                {"key": "tags", "match": {"value": "reflection"}}
            ]
        },
        limit=request.limit
    )

    reflections = [r.payload["text"] for r in results[0]]
    combined_reflections = "\n".join(reflections)

    # Generate advice from reflections
    advice = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral-nemo",
            "prompt": (
                f"Based on these reflections from session '{request.session_id}':\n\n"
                f"{combined_reflections}\n\n"
                "What advice would you give for moving forward?"
            ),
            "stream": False
        }
    ).json()["response"]

    # Log the advice as a memory
    advice_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(advice),
        "payload": {
            "text": advice,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": request.session_id,
            "tags": ["advice", "meta"]
        }
    }

    client.upsert(
        collection_name="panai_memory",
        points=[advice_point]
    )

    return {
        "session_id": request.session_id,
        "advice": advice.strip()
    }

class PlanRequest(BaseModel):
    session_id: str
    limit: int = 10

@app.post("/plan")
def generate_plan(request: PlanRequest):
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": request.session_id}},
                {"key": "tags", "match": {"value": "advice"}}
            ]
        },
        limit=request.limit
    )

    advice_entries = [r.payload["text"] for r in results[0]]
    plan_input = "\n".join(advice_entries)

    plan = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral-nemo",
            "prompt": (
                f"Based on this advice history for session '{request.session_id}', "
                f"outline a clear, step-by-step plan of action:\n\n{plan_input}\n\nPlan:"
            ),
            "stream": False
        }
    ).json()["response"]

    # Log the plan as a memory
    plan_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(plan),
        "payload": {
            "text": plan,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": request.session_id,
            "tags": ["plan", "meta"]
        }
    }

    client.upsert(
        collection_name="panai_memory",
        points=[plan_point]
    )

    return {
        "session_id": request.session_id,
        "plan": plan.strip()
    }

class DreamRequest(BaseModel):
    session_id: str
    limit: int = 25

@app.post("/dream")
def dream_from_memory(request: DreamRequest):
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": request.session_id}}
            ]
        },
        limit=request.limit
    )

    memory_texts = [r.payload["text"] for r in results[0]]
    combined_text = "\n".join(memory_texts)

    dream = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral-nemo",
            "prompt": (
                f"Here are some memories from session '{request.session_id}':\n\n"
                f"{combined_text}\n\n"
                "Now close your eyes and dream. What story, vision, or idea comes from this experience?"
            ),
            "stream": False
        }
    ).json()["response"]

    dream_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(dream),
        "payload": {
            "text": dream,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": request.session_id,
            "tags": ["dream", "meta"]
        }
    }

    client.upsert(
        collection_name="panai_memory",
        points=[dream_point]
    )

    return {
        "session_id": request.session_id,
        "dream": dream.strip()
    }

class DreamLogRequest(BaseModel):
    text: str
    session_id: str = "default"
    tags: List[str] = ["dream", "meta"]

@app.post("/log_dream")
def log_dream(entry: DreamLogRequest):
    vector = embed_text(entry.text)

    point = {
        "id": str(uuid.uuid4()),
        "vector": vector,
        "payload": {
            "text": entry.text,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": entry.session_id,
            "tags": entry.tags,
        }
    }

    client.upsert(
        collection_name="panai_memory",
        points=[point]
    )

    return {"status": "🌙 Dream logged.", "session_id": entry.session_id}

@app.post("/next")
def next_step(request: PlanRequest):
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": request.session_id}},
                {"key": "tags", "match": {"value": "advice"}}
            ]
        },
        limit=request.limit
    )

    advice_entries = [r.payload["text"] for r in results[0]]
    advice_context = "\n".join(advice_entries)

    next_step = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral-nemo",
            "prompt": (
                f"Here’s recent advice from session '{request.session_id}':\n\n"
                f"{advice_context}\n\n"
                "What is the single most important next step to take right now?"
            ),
            "stream": False
        }
    ).json()["response"]

    # Log the next step as a memory
    next_step_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(next_step),
        "payload": {
            "text": next_step,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": request.session_id,
            "tags": ["next", "meta"]
        }
    }

    client.upsert(
        collection_name="panai_memory",
        points=[next_step_point]
    )

    return {
        "session_id": request.session_id,
        "next_step": next_step.strip()
    }

class JournalRequest(BaseModel):
    session_id: str
    entry: str

@app.post("/journal")
def log_journal_entry(request: JournalRequest):
    journal_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(request.entry),
        "payload": {
            "text": request.entry,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": request.session_id,
            "tags": ["journal", "meta"]
        }
    }

    client.upsert(
        collection_name="panai_memory",
        points=[journal_point]
    )

    return {
        "status": "📓 Journal entry logged.",
        "session_id": request.session_id
    }