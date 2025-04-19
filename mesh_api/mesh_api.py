from fastapi import FastAPI, APIRouter
from datetime import datetime
import json
import os

app = FastAPI()
router = APIRouter()

NODES_FILE = "nodes.json"
CHAT_LOG_FILE = "mesh_chat_log.jsonl"

def load_known_peers():
    try:
        with open(NODES_FILE, "r") as f:
            data = json.load(f)
            return data.get("nodes", [])
    except FileNotFoundError:
        return []

def save_peer(peer_entry):
    data = {"nodes": load_known_peers()}
    if not any(p["url"] == peer_entry["url"] for p in data["nodes"]):
        data["nodes"].append(peer_entry)
        with open(NODES_FILE, "w") as f:
            json.dump(data, f, indent=2)

def log_chat_to_mesh(chat_entry):
    with open(CHAT_LOG_FILE, "a") as f:
        f.write(json.dumps(chat_entry) + "\n")

@router.post("/mesh/register_peer")
async def register_peer(peer_data: dict):
    peer_entry = {
        "url": peer_data.get("url"),
        "name": peer_data.get("name", "unknown"),
        "description": peer_data.get("description", ""),
        "version": peer_data.get("version", ""),
        "capabilities": peer_data.get("capabilities", []),
        "values": peer_data.get("values", []),
        "models": peer_data.get("models", {}),
        "ip": peer_data.get("ip", ""),
        "last_seen": datetime.utcnow().isoformat(),
        "status": "ok"
    }
    save_peer(peer_entry)
    return {"message": f"Peer {peer_entry['name']} registered"}

@router.get("/mesh/peers")
async def list_peers():
    peers = load_known_peers()
    return {peer.get("name", "unknown"): peer for peer in peers}

@router.post("/mesh/log_chat")
async def log_chat(chat_data: dict):
    log_chat_to_mesh(chat_data)
    print(f"[DEBUG] Chat data received in /mesh/log_chat:\n{json.dumps(chat_data, indent=2)}")
    try:
        from memory_api.memory_api import log_memory
        print(f"[DEBUG] Logging chat to memory: {json.dumps(chat_data, indent=2)}")
        log_memory(chat_data)
        print("[DEBUG] Chat successfully logged to memory.")
    except Exception as e:
        print(f"[WARN] Could not log chat to memory: {e}")
    print("[DEBUG] Finished processing /mesh/log_chat request.")
    return {"message": "Chat entry logged to mesh"}

app.include_router(router)
