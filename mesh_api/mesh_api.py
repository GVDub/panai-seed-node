from fastapi import APIRouter
from datetime import datetime
import json
import os
import socket

mesh_router = APIRouter()

NODES_FILE = "nodes.json"
CHAT_LOG_FILE = "mesh_chat_log.jsonl"

def load_known_peers():
    if not os.path.exists(NODES_FILE):
        if os.path.exists("nodes_template.json"):
            print("[Mesh] nodes.json not found; initializing from nodes_template.json")
            with open("nodes_template.json", "r") as template_file:
                data = json.load(template_file)
            # Write out to nodes.json
            with open(NODES_FILE, "w") as f:
                json.dump(data, f, indent=2)
            return data.get("nodes", [])
        print("[Mesh] No nodes.json or nodes_template.json found.")
        return []
    with open(NODES_FILE, "r") as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        print("[Mesh] Malformed nodes.json: expected a list under 'nodes'.")
        return []
    return nodes

def save_peer(peer_entry):
    peers = load_known_peers()
    # Update existing or append new
    names = [p.get("name") for p in peers]
    if peer_entry["name"] in names:
        peers = [peer_entry if p.get("name")==peer_entry["name"] else p for p in peers]
    else:
        peers.append(peer_entry)
    # Write back full structure
    out = {"version": "1.0", "nodes": peers}
    with open(NODES_FILE, "w") as f:
        json.dump(out, f, indent=2)

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
                    "text": chat_data.get("response"),
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


# Easter egg endpoint
@mesh_router.get("/easter_egg", operation_id="easter_egg_surprise")
async def easter_egg():
    return {
        "message": "That blowed up real good!",
        "origin": "SCTV",
        "character": "Big Jim McBob & Billy Sol Hurok",
        "note": "Every program needs at least one Easter egg."
    }
