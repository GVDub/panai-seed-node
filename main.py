from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
import os
import requests
from fastapi.responses import JSONResponse
import time
import asyncio
import httpx

import logging

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

start_time = time.time()

# --- Config Loader ---
def load_config(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

identity = load_config("panai.identity.json")
memory = load_config("panai.memory.json")
access = load_config("panai.access.json")

def load_known_peers():
    try:
        with open("nodes.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
known_peers = load_known_peers()

model_name = identity.get("model", "llama3.2:latest")
ollama_url = access.get("ollama_url", "http://localhost:11434/api/chat")

## --- App Setup ---
import socket

def resolve_node_name(identity_json):
    configured_name = identity_json.get("node_name")
    if configured_name in [None, "", "auto"]:
        return f"Seed-{socket.gethostname()}.local"
    return configured_name

app = FastAPI(title=resolve_node_name(identity))
from memory_api.memory_api import router as memory_router
app.include_router(memory_router, prefix="/memory")
from mesh_api.mesh_api import router as mesh_router
app.include_router(mesh_router, prefix="/mesh")

async def preload_models():
    import httpx
    warmup_prompts = [
        {"model": model, "prompt": "Hello", "stream": False}
        for model in identity.get("warmup_models", [])
    ]
    async with httpx.AsyncClient(timeout=30.0) as client:
        for p in warmup_prompts:
            try:
                response = await client.post("http://localhost:11434/api/generate", json=p)
                response.raise_for_status()
                logger.info(f"[Startup] Model {p['model']} warmed up.")
            except httpx.HTTPError as e:
                logger.error(f"[Startup] Warmup failed for {p['model']}: {e}")

async def periodic_health_check():
    await asyncio.sleep(10)  # Give server a moment to fully start
    while True:
        peers = load_known_peers()
        updated = False
        for peer in peers.get("nodes", []):
            url = peer.get("url") or f"http://{peer.get('hostname')}:8000"
            logger.debug(f"[Health Check] Using URL: {url} for peer: {peer.get('hostname')}")
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    r = await client.get(f"{url}/health")
                    r.raise_for_status()
                    health = r.json()
                    peer["status"] = "ok"
                    peer["last_seen"] = datetime.now().isoformat()
                    peer["description"] = health.get("description", "")
                    peer["capabilities"] = health.get("capabilities", [])
                    peer["values"] = health.get("values", [])
                    peer["models"] = health.get("models", {})
                    updated = True
            except Exception:
                peer["status"] = "unreachable"
                logger.warning(f"[Health Check] Peer unreachable: {peer.get('hostname', 'unknown')} ({url})")
                logger.info(f"[Health Check] {peer.get('hostname', 'unknown')} status: {peer['status']}")
        if updated:
            with open("nodes.json", "w") as f:
                json.dump(peers, f, indent=2)
        logger.info(f"[Health Check] Peer statuses: " + ", ".join(f"{p.get('hostname', 'unknown')}: {p.get('status', 'unknown')}" for p in peers.get("nodes", [])))
        logger.info("[Health Check] Completed round of peer health checks.")
        await asyncio.sleep(900)  # 15 minutes

async def periodic_memory_sync():
    await asyncio.sleep(30)  # Let health checks stabilize
    while True:
        peers = load_known_peers()
        for peer in peers.get("nodes", []):
            hostname = peer.get("hostname")
            if not hostname:
                logger.warning(f"[Memory Sync] Skipping peer (no hostname): {peer}")
                continue
            url = peer.get("url") or f"http://{hostname}:8000"
            logger.debug(f"[Memory Sync] Using URL: {url} for peer: {hostname}")
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    r = await client.post(f"{url}/memory/search_by_tag", json={"tags": ["shared", "federated"]})
                    r.raise_for_status()
                    remote_entries = r.json().get("results", [])
                    logger.info(f"[Memory Sync] Retrieved {len(remote_entries)} entries from {hostname}")
                    if len(remote_entries) == 0:
                        logger.warning(f"[Memory Sync] No entries retrieved from {hostname}.")

                    for entry in remote_entries:
                        # Will call into memory_api later for deduplication and storage
                        from memory_api.memory_api import store_synced_memory
                        store_synced_memory(entry)
            except Exception as e:
                logger.error(f"[Memory Sync] Failed to sync with {hostname}: {e}")
        logger.info(f"[Memory Sync] Completed sync cycle with {len(peers.get('nodes', []))} peers.")
        logger.info(f"[Memory Sync] Memory sync stats: " + ", ".join(f"{p.get('hostname', 'unknown')}: {p.get('status', 'unknown')}" for p in peers.get("nodes", [])))
        await asyncio.sleep(1800)  # Sync every 30 minutes

@app.on_event("startup")
async def startup_tasks():
    asyncio.create_task(preload_models())
    asyncio.create_task(periodic_health_check())
    asyncio.create_task(periodic_memory_sync())

# Make sure audit log folder exists
os.makedirs("audit_log", exist_ok=True)

# --- Request/Response Models ---
class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "local"
    tags: list[str] = []

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: str

# --- Logging ---
def log_interaction(prompt, response, tags):
    if not access.get("log_interactions", False):
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"""### [{timestamp}]

**User:** {prompt}

**Model ({model_name}):**  
{response}

**Tags:** {" ".join(f"#{tag}" for tag in tags)}

---
"""
    log_file = f"audit_log/{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(log_file, "a") as f:
        f.write(log_entry)

# --- Chat Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    payload = {
        "model": model_name,
        "prompt": req.prompt,
        "stream": False  # optional, disables token streaming
    }
    try:
        r = requests.post("http://localhost:11434/api/generate", json=payload)
        r.raise_for_status()
        content = r.json()["response"]
    except Exception as e:
        content = f"Error contacting model '{model_name}': {e}"

    log_interaction(req.prompt, content, req.tags)

    return ChatResponse(
        response=content,
        model=model_name,
        timestamp=datetime.now().isoformat()
    )

# --- Node Health Check ---
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "node": resolve_node_name(identity),
        "version": identity.get("version", "unknown"),
        "description": identity.get("description", ""),
        "models": {
            "default": identity.get("models", {}).get("default", "unspecified"),
            "count": len(identity.get("models", {}).get("available", []))
        },
        "capabilities": identity.get("capabilities", []),
        "values": identity.get("values", []),
        "uptime_seconds": int(time.time() - start_time),
        "started_at": datetime.fromtimestamp(start_time).isoformat()
    }

# --- Node Connection Test ---
class NodePingRequest(BaseModel):
    target_url: str

@app.post("/ping_node")
async def ping_node(req: NodePingRequest):
    try:
        r = requests.get(f"{req.target_url}/health", timeout=5)
        r.raise_for_status()
        peer_info = r.json()
        peer_entry = {
            "url": req.target_url,
            "name": peer_info.get("node", "unknown"),
            "description": peer_info.get("description", ""),
            "version": peer_info.get("version", ""),
            "capabilities": peer_info.get("capabilities", []),
            "values": peer_info.get("values", [])
        }

        if not any(p["url"] == peer_entry["url"] for p in known_peers):
            known_peers.append(peer_entry)
            save_peer(peer_entry)

        return {
            "reachable": True,
            "target_url": req.target_url,
            "response": peer_info
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "reachable": False,
                "target_url": req.target_url,
                "error": str(e)
            }
        )

# --- About Endpoint ---
@app.get("/about")
async def about():
    return {
        "identity": identity,
        "access": {k: v for k, v in access.items() if "key" not in k.lower()},
        "model_name": model_name
    }