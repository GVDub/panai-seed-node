from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import asyncio
import httpx
import json
import logging
import os
import requests
import socket
from zeroconf import Zeroconf, ServiceInfo
SERVICE_TYPE = "_panai-memory._tcp.local."
import time

from memory_api.memory_api import (
    log_memory,
    MemoryEntry,
    memory_router,
    stats_router as memory_stats_router
)
from mesh_api.mesh_api import save_peer
from memory_api.memory_api import memory_sync_loop
from mesh_api.mesh_api import mesh_router
from memory_api.prune_synced_logs import prune_synced_logs
from memory_api.qdrant_interface import ensure_panai_memory_collection

from memory_api.memory_logger import log_interaction

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = FastAPI()

logger = logging.getLogger(__name__)

async def schedule_log_cleanup():
    await asyncio.sleep(30)  # Wait a bit after startup
    while True:
        try:
            import aiofiles
            from memory_api.prune_synced_logs import async_prune_synced_logs
            await async_prune_synced_logs("memory_log.json", "cleaned_log.json", days_threshold=30)
            logger.info("[Log Cleanup] Completed scheduled memory log pruning.")
        except Exception as e:
            logger.error(f"[Log Cleanup] Error during log pruning: {e}")
        await asyncio.sleep(259200)  # Every 3 days (in seconds)

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
            data = json.load(f)
        nodes_list = data.get("nodes", [])
        if not isinstance(nodes_list, list):
            print("[Main] Malformed nodes.json: expected a list under 'nodes'.")
            return []
        return nodes_list
    except FileNotFoundError:
        return []
known_peers = load_known_peers()

model_name = identity.get("model", "llama3.2:latest")
ollama_url = access.get("ollama_url", "http://localhost:11434/api/chat")

# --- App Setup ---

def resolve_node_name(identity_json):
    configured_name = identity_json.get("node_name")
    if configured_name in [None, "", "auto"]:
        return f"Seed-{socket.gethostname()}.local"
    return configured_name

app.include_router(memory_router, prefix="/memory")
app.include_router(memory_stats_router, prefix="/memory/stats")
app.include_router(mesh_router, prefix="/mesh")
# Updated for memory router sync check

# --- mDNS Service Registration ---
async def register_mdns_service():
    try:
        zeroconf = Zeroconf()
        service_name = f"{socket.gethostname()}.local."
        service_info = ServiceInfo(
            "_panai-memory._tcp.local.",
            service_name,
            addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
            port=8000,
            properties={b"name": service_name.encode()},
            server=service_name,  # Pass as str, not bytes
        )
        zeroconf.register_service(service_info)
        print(f"[Startup] Registered mDNS service: {service_name}.")
        return zeroconf
    except Exception as e:
        logger.error(f"[Startup] Error registering mDNS service: {e}")

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
        for peer in peers:
            if not isinstance(peer, dict):
                logger.warning(f"[Health Check] Skipping malformed peer entry: {peer}")
                continue
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
                json.dump({"version": "1.0", "nodes": peers}, f, indent=2)
        peer_statuses = ", ".join(
            f"{p.get('hostname', 'unknown')}: {p.get('status', 'unknown')}"
            for p in peers
            if isinstance(p, dict)
        )
        logger.info(f"[Health Check] Peer statuses: {peer_statuses}")
        logger.info("[Health Check] Completed round of peer health checks.")
        await asyncio.sleep(900)  # 15 minutes


@app.on_event("startup")
async def startup_tasks():
    try:
        ensure_panai_memory_collection()
    except Exception as e:
        logger.warning(f"[Startup] Qdrant collection check failed: {e}")
    await register_mdns_service()  # Register mDNS service when the app starts
    asyncio.create_task(preload_models())
    asyncio.create_task(periodic_health_check())
    asyncio.create_task(memory_sync_loop())
    asyncio.create_task(schedule_log_cleanup())
    logger.info("[Startup] All background tasks launched. Monitoring peers and memory sync.")

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

# --- Chat Endpoint ---
@app.post("/chat", response_model=ChatResponse, operation_id="chat_with_model")
async def chat(req: ChatRequest):
    payload = {
        "model": model_name,
        "prompt": req.prompt,
        "stream": False  # optional, disables token streaming
    }
    try:
        r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=10)
        r.raise_for_status()
        content = r.json()["response"]
    except Exception as e:
        content = f"Error contacting model '{model_name}': {e}"

    log_interaction(req.prompt, content, req.tags, access, model_name)

    return ChatResponse(
        response=content,
        model=model_name,
        timestamp=datetime.now().isoformat()
    )

# --- Node Health Check ---
@app.get("/health", operation_id="health_check_status")
async def health_check():
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient("localhost", port=6333)
        collections = client.get_collections().collections
        memory_ok = any(c.name == "panai_memory" for c in collections)
    except Exception as e:
        memory_ok = False
        logger.error(f"[Health Check] Qdrant memory check failed: {e}")

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
        "started_at": datetime.fromtimestamp(start_time).isoformat(),
        "memory_status": "ok" if memory_ok else "missing"
    }

# --- Node Connection Test ---
class NodePingRequest(BaseModel):
    target_url: str

@app.post("/ping_node", operation_id="ping_peer_node")
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
@app.get("/about", operation_id="about_node_info")
async def about():
    return {
        "identity": identity,
        "access": {k: v for k, v in access.items() if "key" not in k.lower()},
        "model_name": model_name
    }

@app.post("/store", operation_id="store_memory_alias")
async def store_alias(req: MemoryEntry):
    return await log_memory(req)

@app.post("/trigger_manual_memory_sync", operation_id="manual_memory_sync")
async def trigger_manual_memory_sync():
    await memory_sync_loop()
    return {"status": "Manual memory sync triggered"}

logger.info(f"[Startup] {resolve_node_name(identity)} is now live and ready.")