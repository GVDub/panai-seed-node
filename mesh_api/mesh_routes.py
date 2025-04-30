

from fastapi import APIRouter, Request
from mesh_api.peer_registry import save_peer, load_known_peers
from mesh_api.mesh_utils import log_chat_to_mesh
from datetime import datetime
import httpx
import json

router = APIRouter()

@router.post("/mesh/register_peer")
async def register_peer(request: Request):
    data = await request.json()
    save_peer(data)
    return {"status": "ok", "message": "Peer registered"}

@router.get("/mesh/list_peers")
async def list_peers():
    peers = load_known_peers()
    return {"status": "ok", "peers": peers}

@router.post("/mesh/log_chat")
async def log_chat(request: Request):
    payload = await request.json()
    log_chat_to_mesh(payload)
    return {"status": "ok", "message": "Chat log received"}

@router.get("/mesh/easter_egg")
async def easter_egg():
    return {"message": "🤖🐣 Mesh API active. The network is watching..."}


# Make mesh_routes available for import
mesh_routes = router