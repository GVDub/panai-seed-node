from fastapi import APIRouter
from datetime import datetime
import json
import os

mesh_router = APIRouter()

NODES_FILE = "nodes.json"
CHAT_LOG_FILE = "mesh_chat_log.jsonl"

def load_known_peers():
    try:
        with open(NODES_FILE, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}

def save_peer(peer_entry):
    data = load_known_peers()
    if peer_entry["name"] not in data:
        data[peer_entry["name"]] = peer_entry
        with open(NODES_FILE, "w") as f:
            json.dump(data, f, indent=2)

def log_chat_to_mesh(chat_entry):
    with open(CHAT_LOG_FILE, "a") as f:
        f.write(json.dumps(chat_entry) + "\n")

@mesh_router.post("/register_peer", operation_id="register_peer_node")
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

@mesh_router.get("/peers", operation_id="list_known_peers")
async def list_peers():
    peers = load_known_peers()
    return peers

@mesh_router.post("/log_chat", operation_id="log_chat_to_memory_mesh")
async def log_chat(chat_data: dict):
    log_chat_to_mesh(chat_data)
    print(f"[DEBUG] Chat data received in /mesh/log_chat:\n{json.dumps(chat_data, indent=2)}")
    import httpx
    print(f"[DEBUG] Logging chat to memory via internal POST: {json.dumps(chat_data, indent=2)}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/memory/log_memory",
                json={
                    "text": chat_data.get("text"),
                    "session_id": chat_data.get("session_id"),
                    "tags": chat_data.get("tags", [])
                },
                timeout=5.0
            )
            response.raise_for_status()
        print("[DEBUG] Chat successfully logged to memory.")
    except Exception as e:
        print(f"[WARN] Could not log chat to memory: {e}")
    print("[DEBUG] Finished processing /mesh/log_chat request.")
    return {"message": "Chat entry logged to mesh"}

router = mesh_router
