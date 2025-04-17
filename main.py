from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
import os
import requests
from fastapi.responses import JSONResponse
import time
start_time = time.time()

# --- Config Loader ---
def load_config(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

identity = load_config("panai.identity.json")
memory = load_config("panai.memory.json")
access = load_config("panai.access.json")

model_name = identity.get("model", "llama3")
ollama_url = access.get("ollama_url", "http://localhost:11434/api/chat")

## --- App Setup ---
import socket

def resolve_node_name(identity_json):
    configured_name = identity_json.get("node_name")
    if configured_name in [None, "", "auto"]:
        return f"Seed-{socket.gethostname()}"
    return configured_name

app = FastAPI(title=resolve_node_name(identity))
from memory_api.memory_api import router as memory_router
app.include_router(memory_router, prefix="/memory")
@app.on_event("startup")
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
                print(f"[Startup] Model {p['model']} warmed up.")
            except httpx.HTTPError as e:
                print(f"[Startup] Warmup failed for {p['model']}: {e}")

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
        return {
            "reachable": True,
            "target_url": req.target_url,
            "response": r.json()
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