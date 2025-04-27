# Utility: Normalize peer URL for consistent identity checks
def normalize_peer_url(url: str) -> str:
    try:
        if url.startswith("http://") or url.startswith("https://"):
            scheme, rest = url.split("://", 1)
        else:
            scheme, rest = "http", url
        host_port = rest.split("/", 1)[0]
        host, *port = host_port.split(":")
        ip = socket.gethostbyname(host)
        return f"{scheme}://{ip}:{port[0] if port else '8000'}"
    except Exception as e:
        print(f"[WARN] Could not normalize peer URL '{url}': {e}")
        return url  # fallback to original
# Standard library imports
from typing import List
from datetime import datetime
from datetime import timezone
import uuid
import asyncio
import httpx
import os
import json
#third-party imports
from fastapi import FastAPI, APIRouter, Request
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import socket

# Zeroconf/mDNS imports for LAN peer discovery
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange
SERVICE_TYPE = "_panai-memory._tcp.local."

import requests
import torch
torch.set_num_threads(14)  # Reserve 1–2 threads for system processes

memory_router = APIRouter()
stats_router = APIRouter()

# Ensure memory_log.json exists
if not os.path.exists("memory_log.json"):
    with open("memory_log.json", "w") as f:
        json.dump([], f)

client = QdrantClient(host="localhost", port=6333)

# Load all-mpnet-base-v2 model for embedding (768-dimension)
embed_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")




def embed_text(text: str) -> list:
    try:
        vector = embed_model.encode(text, normalize_embeddings=True).tolist()
        if not vector or len(vector) != 768:
            print(f"[Embedding ERROR] Invalid vector — len={len(vector) if vector else 'None'} — text='{text[:50]}'")
        else:
            print(f"[Embedding OK] Vector len={len(vector)} for text: '{text[:50]}'")
        return vector
    except Exception as e:
        print(f"[Embedding EXCEPTION] Failed to embed: {text[:50]} — {e}")
        return None

# --- Begin get_local_identity function ---
def get_local_identity():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())
# --- End get_local_identity function ---

def log_generic_memory(text: str, session_id: str, tags: List[str]):
    if not text.strip():
        print(f"[Validation] Skipping memory with empty text.")
        return None
    if not session_id.strip():
        print(f"[Validation] Skipping memory with empty session_id.")
        return None
    # Deduplication check before embedding
    existing = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": session_id}},
                {"key": "text", "match": {"value": text}}
            ]
        },
        limit=1
    )

    if existing and existing[0]:
        print(f"[Deduplication] Skipping duplicate memory: {text[:50]}...")
        return None

    vector = embed_text(text)
    self_host = socket.gethostname()
    local_peer_tag = f"synced:http://{get_local_identity()}:8000"
    point = {
        "id": str(uuid.uuid4()),
        "vector": vector,
        "payload": {
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "tags": list(set(tag.lower() for tag in tags + [session_id, local_peer_tag])),
        }
    }
    client.upsert(collection_name="panai_memory", points=[point])
    # Also append to memory_log.json for testing/dev visibility
    try:
        with open("memory_log.json", "r+") as f:
            try:
                log = json.load(f)
                if not isinstance(log, list):
                    raise ValueError("memory_log.json does not contain a list.")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[Warning] memory_log.json parse error: {e}. Reinitializing log.")
                log = []
            log.append(point["payload"])
            f.seek(0)
            json.dump(log, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[Warning] Could not write to memory_log.json: {e}")
    return point["id"]

def query_and_generate(session_id: str, tags: List[str], prompt_template: str, model: str = "mistral-nemo", limit: int = 25) -> str:
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": session_id}},
                *([{"key": "tags", "match": {"value": tag}} for tag in tags] if tags else [])
            ]
        },
        limit=limit
    )
    memory_texts = [r.payload["text"] for r in results[0]]
    combined_text = "\n".join(memory_texts)
    prompt = prompt_template.format(session_id=session_id, combined_text=combined_text)
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    ).json()["response"]
    return response

async def query_and_generate_async(session_id: str, tags: List[str], prompt_template: str, model: str = "mistral-nemo", limit: int = 25) -> str:
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": session_id}},
                *([{"key": "tags", "match": {"value": tag}} for tag in tags] if tags else [])
            ]
        },
        limit=limit
    )
    memory_texts = [r.payload["text"] for r in results[0]]
    combined_text = "\n".join(memory_texts)
    prompt = prompt_template.format(session_id=session_id, combined_text=combined_text)
    
    async with httpx.AsyncClient(timeout=180.0) as http_client:
        try:
            response = await http_client.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
            response.raise_for_status()
            return response.json()["response"]
        except httpx.HTTPError as e:
            print(f"[ERROR] HTTP error during LLM call: {e}")
            return f"❌ Error from language model: {e}"

class MemoryEntry(BaseModel):
    text: str
    session_id: str = "default"
    tags: List[str] = []

class QueryRequest(BaseModel):
    vector: list
    limit: int = 1

class TextQuery(BaseModel):
    text: str
    limit: int = 1

class TagQuery(BaseModel):
    tags: List[str]
    limit: int = 5
    
class SummaryRequest(BaseModel):
    session_id: str
    limit: int = 20  # number of memories to summarize    

@memory_router.post("/search", operation_id="search_memory_vector")
def search_memory(request: QueryRequest):
    results = client.search(
        collection_name="panai_memory",
        query_vector=request.vector,
        limit=request.limit
    )
    return {"results": [r.payload for r in results]}

@memory_router.post("/recall", operation_id="recall_memory_by_text")
def recall_from_text(request: TextQuery):
    embedded_vector = embed_text(request.text)
    results = client.search(
        collection_name="panai_memory",
        query_vector=embedded_vector,
        limit=request.limit
    )
    return {"results": [r.payload for r in results]}


@memory_router.post("/search_by_tag", operation_id="search_memory_by_tag")
def search_by_tag(request: TagQuery, req: Request):
    print(f"[TAG SEARCH] From {req.client.host}, Tags: {request.tags}")
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                *([{"key": "tags", "match": {"value": tag.lower()}} for tag in request.tags] if request.tags else [])
            ]
        },
        limit=request.limit
    )
    return {"results": [r.payload for r in results[0]]}

class MemoryLog(BaseModel):
    text: str
    session_id: str = "default"
    tags: List[str] = []

@memory_router.post("/memory/log_memory", operation_id="log_memory")
def log_memory(entry: MemoryLog):
    log_generic_memory(entry.text, entry.session_id, entry.tags)
    return {"status": "🧠 Memory logged.", "session_id": entry.session_id}

@memory_router.post("/memory/store", operation_id="store_memory")
def store_memory_alias(entry: MemoryLog):
    return log_memory(entry)

@memory_router.post("/memory/summarize", operation_id="summarize_session")
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

@memory_router.post("/memory/reflect", operation_id="reflect_on_session")
async def reflect_on_session(request: ReflectRequest):
    prompt_template = (
        "Here is a series of memory logs from session '{session_id}':\n\n"
        "{combined_text}\n\n"
        "Reflect on these memories. What patterns, concerns, or deeper insights emerge?"
    )
    reflection = await query_and_generate_async(request.session_id, [], prompt_template)
    reflection_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(reflection),
        "payload": {
            "text": reflection,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": request.session_id,
            "tags": ["reflection", "meta"]
        }
    }
    client.upsert(collection_name="panai_memory", points=[reflection_point])
    return {"session_id": request.session_id, "reflection": reflection.strip()}

class AdviceRequest(BaseModel):
    session_id: str
    limit: int = 10

@memory_router.post("/memory/advice", operation_id="give_advice")
async def give_advice(request: AdviceRequest):
    prompt_template = (
        "Based on these reflections from session '{session_id}':\n\n"
        "{combined_text}\n\n"
        "What advice would you give for moving forward?"
    )
    advice = await query_and_generate_async(request.session_id, ["reflection"], prompt_template, limit=request.limit)
    advice_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(advice),
        "payload": {
            "text": advice,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": request.session_id,
            "tags": ["advice", "meta"]
        }
    }
    client.upsert(collection_name="panai_memory", points=[advice_point])
    return {"session_id": request.session_id, "advice": advice.strip()}

class PlanRequest(BaseModel):
    session_id: str
    limit: int = 10

@memory_router.post("/memory/plan", operation_id="generate_plan")
async def generate_plan(request: PlanRequest):
    prompt_template = (
        "Based on this advice history for session '{session_id}', "
        "outline a clear, step-by-step plan of action:\n\n{combined_text}\n\nPlan:"
    )
    plan = await query_and_generate_async(request.session_id, ["advice"], prompt_template, limit=request.limit)
    plan_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(plan),
        "payload": {
            "text": plan,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": request.session_id,
            "tags": ["plan", "meta"]
        }
    }
    client.upsert(collection_name="panai_memory", points=[plan_point])
    return {"session_id": request.session_id, "plan": plan.strip()}

class DreamRequest(BaseModel):
    session_id: str
    limit: int = 25

@memory_router.post("/memory/dream", operation_id="dream_from_memory")
async def dream_from_memory(request: DreamRequest):
    prompt_template = (
        "Here are some memories from session '{session_id}':\n\n"
        "{combined_text}\n\n"
        "Now close your eyes and dream. What story, vision, or idea comes from this experience?"
    )
    dream = await query_and_generate_async(request.session_id, [], prompt_template, limit=request.limit)
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

@memory_router.post("/memory/log_dream", operation_id="log_dream")
def log_dream(entry: DreamLogRequest):
    log_generic_memory(entry.text, entry.session_id, entry.tags)
    return {"status": "🌙 Dream logged.", "session_id": entry.session_id}

class ReflectionLogRequest(BaseModel):
    text: str
    session_id: str = "default"
    tags: List[str] = ["reflection", "meta"]

@memory_router.post("/memory/log_reflection", operation_id="log_reflection")
def log_reflection(entry: ReflectionLogRequest):
    log_generic_memory(entry.text, entry.session_id, entry.tags)
    return {"status": "🔍 Reflection logged.", "session_id": entry.session_id}

class AdviceLogRequest(BaseModel):
    text: str
    session_id: str = "default"
    tags: List[str] = ["advice", "meta"]

@memory_router.post("/memory/log_advice", operation_id="log_advice")
def log_advice(entry: AdviceLogRequest):
    log_generic_memory(entry.text, entry.session_id, entry.tags)
    return {"status": "💡 Advice logged.", "session_id": entry.session_id}

class PlanLogRequest(BaseModel):
    text: str
    session_id: str = "default"
    tags: List[str] = ["plan", "meta"]

@memory_router.post("/memory/log_plan", operation_id="log_plan")
def log_plan(entry: PlanLogRequest):
    log_generic_memory(entry.text, entry.session_id, entry.tags)
    return {"status": "🧭 Plan logged.", "session_id": entry.session_id}

@memory_router.post("/memory/next", operation_id="generate_next_step")
async def next_step(request: PlanRequest):
    prompt_template = (
        "Here’s recent advice from session '{session_id}':\n\n"
        "{combined_text}\n\n"
        "What is the single most important next step to take right now?"
    )
    next_step = await query_and_generate_async(request.session_id, ["advice"], prompt_template, limit=request.limit)
    next_step_point = {
        "id": str(uuid.uuid4()),
        "vector": embed_text(next_step),
        "payload": {
            "text": next_step,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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

@memory_router.post("/memory/journal", operation_id="log_journal_entry")
def log_journal_entry(request: JournalRequest):
    log_generic_memory(request.entry, request.session_id, ["journal", "meta"])
    return {
        "status": "📓 Journal entry logged.",
        "session_id": request.session_id
    }

class SyncRequest(BaseModel):
    peer_url: str
    tags: List[str] = []
    session_id: str | None = None
    limit: int = 10

@memory_router.post("/sync_with_peer", operation_id="sync_with_peer")
async def sync_with_peer(req: SyncRequest):
    # Prevent self-syncing based on peer_url
    local_hostnames = {socket.gethostname(), socket.getfqdn(), "localhost"}
    peer_url = normalize_peer_url(req.peer_url)
    print("Received sync_with_peer request")
    print(f"Request contents: {req}")
    if req.peer_url:
        peer_host = req.peer_url.replace("http://", "").replace("https://", "").split(":")[0]
        if peer_host in local_hostnames:
            print(f"[SyncWithPeer] Skipping self-sync with {req.peer_url}")
            return {"peer": req.peer_url, "attempted": 0, "synced": 0}

    matching = []

    # Build scroll_filter using new logic
    scroll_filter = {}

    # Default to broad inclusion if session_id and tags not provided
    must_conditions = []
    if req.session_id:
        must_conditions.append({"key": "session_id", "match": {"value": req.session_id}})
    # If no session_id is provided, allow pulling from all sessions (no forced 'default')

    scroll_filter["must"] = must_conditions
    print(f"[DEBUG] Sync filter being applied:\n{json.dumps(scroll_filter, indent=2)}")

    if req.tags:
        scroll_filter["should"] = [{"key": "tags", "match": {"value": tag.lower()}} for tag in req.tags]

    # Always exclude entries already synced to this peer
    if req.peer_url:
        exclude_tag = f"synced:{peer_url}"
        scroll_filter["must_not"] = [{"key": "tags", "match": {"value": exclude_tag}}]

    # Print sync request details
    print(f"[SyncWithPeer] Received sync request from {req.peer_url} — Tags: {req.tags}, Session: {req.session_id}")

    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter=scroll_filter,
        limit=req.limit,
        with_vectors=True
    )
    print(f"[DEBUG] Found {len(results[0])} candidate entries for sync before final tag checks.")
    for p in results[0]:
        print(f"[DEBUG] Entry ID={p.id}, session={p.payload.get('session_id')}, tags={p.payload.get('tags', [])}")
    for point in results[0]:
        matching.append({
            "id": point.id,
            "vector": point.vector,
            "text": point.payload.get("text", ""),
            "session_id": point.payload["session_id"],
            "tags": point.payload.get("tags", [])
        })

    # The old logic 'for mem in all_memories:' has been replaced by the filtered 'matching' entries above.
    # No further broad iteration is needed; all sync and skip logic is now handled per-matching entry.

    # Add counters for skipped entries and reasons
    skipped_vectorless = 0
    skipped_already_synced = 0

    successes = 0
    async with httpx.AsyncClient(timeout=10.0) as client_async:
        for entry in matching:
            # Improved logic: check for any "synced:" tags, and specifically if already synced to this peer
            existing_synced_tags = [tag for tag in entry["tags"] if tag.startswith("synced:")]
            if f"synced:{peer_url}" in existing_synced_tags:
                print(f"[DEBUG] Entry already synced to {peer_url}, skipping.")
                skipped_already_synced += 1
                continue

            # Skip if vector is missing
            if entry.get("vector") is None:
                print(f"[DEBUG] Skipping memory without vector: {entry['text'][:50]}")
                skipped_vectorless += 1
                continue

            try:
                # Begin constructing peer endpoint
                peer_endpoint = req.peer_url
                if not peer_endpoint.startswith("http://") and not peer_endpoint.startswith("https://"):
                    peer_endpoint = f"http://{peer_endpoint}"
                res = await client_async.post(f"{peer_endpoint}/memory/log_memory", json=entry)
                res.raise_for_status()
                # After successful sync, update the entry's tags if not already present
                tag = f"synced:{peer_url}"
                if tag not in entry["tags"]:
                    entry["tags"].append(tag)
                    client.upsert(
                        collection_name="panai_memory",
                        points=[{
                            "id": entry["id"],
                            "vector": entry["vector"],
                            "payload": {
                                "text": entry["text"],
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "session_id": entry["session_id"],
                                "tags": entry["tags"]
                            }
                        }]
                    )
                successes += 1
            except Exception as e:
                print(f"Failed to sync memory entry: {e}")

    print(f"[Memory Sync] Synced {successes}/{len(matching)} entries to {req.peer_url}")
    # Print attempted/successful sync before returning
    print(f"[SyncWithPeer] Attempted {len(matching)}, synced {successes} to {req.peer_url}")
    print(f"[SyncWithPeer] Skipped {skipped_vectorless} entries without vectors.")
    print(f"[SyncWithPeer] Skipped {skipped_already_synced} entries already tagged as synced.")
    return {
        "peer": req.peer_url,
        "attempted": len(matching),
        "synced": successes,
    }

def store_synced_memory(entry: dict):
    """Store a memory entry from a peer, avoiding duplicates by hash of text + session_id."""

    text = entry.get("text", "")
    session_id = entry.get("session_id", "default")
    tags = entry.get("tags", [])

    if not text:
        return

    # Check if a memory with same hash exists
    existing = client.scroll(
        collection_name="panai_memory",
        scroll_filter={
            "must": [
                {"key": "session_id", "match": {"value": session_id}},
                {"key": "text", "match": {"value": text}}
            ]
        },
        limit=1
    )

    if existing[0]:
        print(f"[Memory Sync] Skipping duplicate: {text[:40]}...")
        return

    # Otherwise, embed and store it
    vector = embed_text(text)
    point = {
        "id": str(uuid.uuid4()),
        "vector": vector,
        "payload": {
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "tags": tags
        }
    }
    client.upsert(collection_name="panai_memory", points=[point])
    # print(f"[Memory Sync] Stored: {text[:40]}...")

@stats_router.get("/admin/memory_stats", operation_id="memory_stats")
def memory_stats():
    try:
        count = client.count(collection_name="panai_memory", exact=True).count
        return {
            "collection": "panai_memory",
            "total_memories": count,
            "status": "ok"
        }
    except Exception as e:
        return {
            "collection": "panai_memory",
            "status": "error",
            "message": str(e)
        }

@memory_router.post("/mesh/log_chat", operation_id="log_chat_to_mesh")
def log_chat_to_mesh(entry: MemoryEntry):
    log_generic_memory(entry.text, entry.session_id, entry.tags)
    return {"status": "🌐 Chat memory logged to mesh.", "session_id": entry.session_id}

# Background memory sync loop
 

async def sync_all_peers():
    """Perform memory sync with all known peers."""
    import json
    import os

    # ZeroConf mDNS discovery for local LAN peers
    local_peers = set()
    def on_service_state_change(zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info and info.addresses:
                ip = socket.inet_ntoa(info.addresses[0])
                # skip self by IP
                if ip != socket.gethostbyname(socket.gethostname()):
                    local_peers.add(f"{ip}:8000")
    zeroconf = Zeroconf()
    browser = ServiceBrowser(zeroconf, SERVICE_TYPE, handlers=[on_service_state_change])
    # Give mDNS a moment to discover peers
    await asyncio.sleep(2)
    zeroconf.close()
    # Filter out localhost variants from mDNS-discovered peers
    local_peers = {peer for peer in local_peers if not peer.startswith("127.") and "localhost" not in peer}
    print(f"[Memory Sync] Discovered LAN peers via mDNS: {local_peers}")

    nodes_file = os.path.join(os.path.dirname(__file__), "..", "nodes.json")
    if not os.path.exists(nodes_file):
        print(f"[Memory Sync] nodes.json not found at expected path: {nodes_file}")
        return

    with open(nodes_file, "r") as f:
        data = json.load(f)
    nodes_list = data.get("nodes", [])
    print(f"[DEBUG] 🧪 sync_all_peers running on {os.uname().nodename}")
    print(f"[DEBUG] nodes field type = {type(nodes_list)}")

    if not isinstance(nodes_list, list):
        print("[Memory Sync] Malformed nodes.json: expected a list under 'nodes'.")
        return

    # Debug print: node status and services
    for node in nodes_list:
        # Use 'hostname' if present, else fallback to 'ip' or 'name'
        host = node.get('hostname')
        if not host:
            host = node.get('ip') or node.get('name') or 'UNKNOWN_HOST'
            print(f"[Memory Sync WARNING] Node entry missing 'hostname'. Using fallback: {host}. Node: {node}")
        else:
            print(f"[Memory Sync] Node '{host}': status={node.get('status')}, services={node.get('services')}")

    # Determine local hostnames to exclude self from peer list
    local_short = socket.gethostname()
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()
    local_fqdn = get_local_ip()
    local_names = {local_short, local_fqdn, "localhost"}
    print(f"[Memory Sync] Local host names: short={local_short}, fqdn={local_fqdn}")

    # Determine local base URL for peer sync (reporting to peers)
    local_base_url = f"http://{local_fqdn}:8000"
    print(f"[Memory Sync] Using local base URL: {local_base_url}")

    # Include all nodes with the "memory" service, excluding self and local aliases
    peer_urls = []
    for node in nodes_list:
        # Use 'hostname' if present, else fallback to 'ip' or 'name'
        hostname = node.get("hostname")
        peer_display = None
        if not hostname:
            # Try fallback to ip or name
            hostname = node.get("ip")
            if hostname:
                peer_display = f"[Fallback to IP] {hostname}"
            else:
                hostname = node.get("name")
                if hostname:
                    peer_display = f"[Fallback to 'name'] {hostname}"
                else:
                    print(f"[Memory Sync WARNING] Node entry missing both 'hostname', 'ip', and 'name': {node}")
                    continue
        else:
            peer_display = hostname
        # --- Begin IP fallback logic ---
        # Try to resolve hostname; if fails, fallback to IP
        original_hostname = hostname
        try:
            socket.gethostbyname(hostname)
        except socket.gaierror:
            hostname = node.get("ip")
            print(f"[Memory Sync] Fallback to IP: {hostname}")
        # --- End IP fallback logic ---
        # skip nodes without the memory service
        if "memory" not in node.get("services", []):
            continue
        # skip if hostname contains any local identifier
        if any(local_name in hostname for local_name in local_names):
            print(f"[Memory Sync] Excluding self or local alias: {hostname}")
            continue
        print(f"[Memory Sync] Preparing to sync with peer: {peer_display}")
        peer_urls.append(hostname)
    print(f"[Memory Sync] Target peer URLs for sync: {peer_urls}")

    # Merge dynamic LAN peers with static nodes.json peers
    combined_peers = list(local_peers) + [url for url in peer_urls if url not in local_peers]
    print(f"[Memory Sync] Combined peer URLs: {combined_peers}")

    async def sync_peer(peer):
        if peer:
            # Ensure default port 8000 for peer sync endpoint
            host = peer
            if ":" not in peer:
                host = f"{peer}:8000"
            url = f"http://{host}/memory/sync_with_peer"
            try:
                async with httpx.AsyncClient(timeout=10.0) as client_async:
                    peer_endpoint = url
                    if not peer_endpoint.startswith("http://") and not peer_endpoint.startswith("https://"):
                        peer_endpoint = f"http://{peer_endpoint}"
                    print(f"[Memory Sync] Syncing with peer at {peer_endpoint}")
                    res = await client_async.post(
                        url,
                        json={"peer_url": local_base_url, "session_id": "", "tags": [], "limit": 10}
                    )
                    res.raise_for_status()
            except Exception as e:
                print(f"[Memory Sync] Failed to sync with {url}: {e}")

    await asyncio.gather(*(sync_peer(peer) for peer in combined_peers))
    # print(f"[Memory Sync Loop] {datetime.utcnow().isoformat()} - Peer sync completed.")

async def memory_sync_loop():
    """Periodically sync memory entries with known peers."""
    print("[Memory Sync Loop] Performing initial sync...")
    try:
        print(f"[Memory Sync Loop] About to run sync_all_peers at {datetime.utcnow().isoformat()}")
        await sync_all_peers()  # <-- run initial sync at startup
        print(f"[Memory Sync Loop] sync_all_peers finished at {datetime.utcnow().isoformat()}")
        print(f"[Memory Sync Loop] {datetime.utcnow().isoformat()} - Initial sync complete.")
    except Exception as e:
        print(f"[Memory Sync Loop] ERROR during initial sync: {e}")

    while True:
        try:
            print(f"[Memory Sync Loop] {datetime.utcnow().isoformat()} - Sleeping 5 minutes...")
            await asyncio.sleep(300)
            print(f"[Memory Sync Loop] {datetime.utcnow().isoformat()} - Running periodic sync...")
            print(f"[Memory Sync Loop] About to run sync_all_peers at {datetime.utcnow().isoformat()}")
            await sync_all_peers()
            print(f"[Memory Sync Loop] sync_all_peers finished at {datetime.utcnow().isoformat()}")
            print(f"[Memory Sync Loop] {datetime.utcnow().isoformat()} - Periodic sync complete.")
        except Exception as e:
            print(f"[Memory Sync Loop] ERROR: {e}")

__all__ = ["memory_router", "stats_router", "log_memory", "store_synced_memory", "MemoryEntry", "log_chat_to_mesh", "memory_sync_loop", "sync_all_peers"]


@stats_router.get("/admin/dump_memories", operation_id="dump_memories")
def dump_all_memories(limit: int = 20):
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={},  # no filter
        limit=limit,
        with_vectors=True  # <-- Ensure vectors are returned
    )
    return {
        "count": len(results[0]),
        "entries": [
            {
                "text": p.payload.get("text", "")[:80],
                "session_id": p.payload.get("session_id", ""),
                "tags": p.payload.get("tags", []),
                "id": p.id
            } for p in results[0]
        ]
    }

# ADMIN: Re-embed missing vectors
# Qdrant does not support filtering on null/missing vectors directly.
# As a workaround, this endpoint will fetch the first `limit` entries (with no filter)
# and attempt to re-embed those whose vector is missing or None.
@stats_router.post("/admin/reembed_missing", operation_id="reembed_missing")
def reembed_missing(limit: int = 100):
    results = client.scroll(
        collection_name="panai_memory",
        scroll_filter={},  # Qdrant does not support 'vector is None' filter directly
        limit=limit,
        with_vectors=True  # <-- Ensure vectors are returned
    )
    reembedded = 0
    skipped = 0
    for point in results[0]:
        # Only re-embed if vector is missing or None or empty
        vector = getattr(point, "vector", None)
        print(f"[DEBUG] Point ID={point.id}, vector present={bool(vector)} len={len(vector) if vector else 'None'}")
        if vector is not None and isinstance(vector, list) and len(vector) > 0:
            continue
        text = point.payload.get("text", "")
        session_id = point.payload.get("session_id", "default")
        tags = point.payload.get("tags", [])
        if not text:
            skipped += 1
            continue
        try:
            vector = embed_text(text)
            client.upsert(
                collection_name="panai_memory",
                points=[{
                    "id": point.id,
                    "vector": vector,
                    "payload": {
                        "text": text,
                        "timestamp": point.payload.get("timestamp"),
                        "session_id": session_id,
                        "tags": tags
                    }
                }]
            )
            reembedded += 1
        except Exception as e:
            # print(f"[ERROR] Failed to re-embed: {text[:40]}... | {e}")
            skipped += 1

    message = "No missing vectors found." if reembedded == 0 else "Re-embedding complete."
    return {
        "status": f"✅ {message}",
        "reembedded": reembedded,
        "skipped": skipped
    }

@memory_router.on_event("startup")
async def start_background_tasks():
    print("[Startup] Entered start_background_tasks() and launching memory sync background task.")

    # Ensure nodes.json is created from template if missing
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_path = os.path.join(base_dir, "nodes_template.json")
    nodes_path = os.path.join(base_dir, "nodes.json")

    if not os.path.exists(nodes_path) and os.path.exists(template_path):
        try:
            with open(template_path, "r") as src, open(nodes_path, "w") as dst:
                dst.write(src.read())
            print(f"[Startup] Copied nodes_template.json to nodes.json at: {nodes_path}")
        except Exception as e:
            print(f"[Startup ERROR] Failed to copy nodes_template.json: {e}")
    else:
        print(f"[Startup] nodes.json already exists or template is missing.")

    # Explicitly print confirmation if nodes.json is not being created
    if not os.path.exists(nodes_path):
        print(f"[Startup WARNING] nodes.json was expected to be created but is still missing at: {nodes_path}")
    elif os.path.exists(nodes_path):
        print(f"[Startup OK] nodes.json confirmed present at: {nodes_path}")
        # Additional check to validate the content of nodes.json
        try:
            with open(nodes_path, "r") as f:
                data = json.load(f)
            if "nodes" not in data or not isinstance(data["nodes"], list):
                print(f"[Startup WARNING] nodes.json is present but 'nodes' key is missing or malformed.")
        except Exception as e:
            print(f"[Startup ERROR] Failed to load nodes.json: {e}")

    # Ensure memory_log.json is valid JSON list, else reinitialize
    log_path = os.path.join(base_dir, "memory_log.json")
    try:
        with open(log_path, "r+") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("memory_log.json does not contain a list.")
    except Exception as e:
        print(f"[Startup] Reinitializing corrupt memory_log.json: {e}")
        with open(log_path, "w") as f:
            json.dump([], f)

    asyncio.create_task(memory_sync_loop())