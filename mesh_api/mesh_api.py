from fastapi import FastAPI
from fastapi import APIRouter
from datetime import datetime

app = FastAPI()
router = APIRouter()

peers = {}

@router.post("/mesh/register_peer")
async def register_peer(peer_data: dict):
    peer_id = peer_data.get("node", "unknown")
    peers[peer_id] = {
        "last_seen": datetime.utcnow().isoformat(),
        "status": peer_data.get("status", "unknown"),
        "description": peer_data.get("description", ""),
        "capabilities": peer_data.get("capabilities", []),
        "values": peer_data.get("values", []),
        "models": peer_data.get("models", {}),
        "ip": peer_data.get("ip", "")
    }
    return {"message": f"Peer {peer_id} registered"}

@router.get("/mesh/peers")
async def list_peers():
    return peers

app.include_router(router)
