from fastapi import FastAPI, APIRouter
from datetime import datetime
import json
import os

app = FastAPI()
router = APIRouter()

NODES_FILE = "nodes.json"

def load_known_peers():
    try:
        with open(NODES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_peer(peer_entry):
    peers = load_known_peers()
    if not any(p["url"] == peer_entry["url"] for p in peers):
        peers.append(peer_entry)
        with open(NODES_FILE, "w") as f:
            json.dump(peers, f, indent=2)

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
    return {peer.get("name", "unknown"): peer for peer in load_known_peers()}

app.include_router(router)
