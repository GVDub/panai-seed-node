from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
import os
import requests
from fastapi.responses import JSONResponse

# --- Config Loader ---
def load_config(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

identity = load_config("panai.identity.json")
memory = load_config("panai.memory.json")
access = load_config("panai.access.json")

model_name = identity.get("model", "llama3")
ollama_url = "http://localhost:11434/api/chat"

# --- App Setup ---
app = FastAPI(title=identity.get("node_name", "seed-node"))
from memory_api.routes import router as memory_router
app.include_router(memory_router, prefix="/memory")

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
        content = f"Error contacting model: {e}"

    log_interaction(req.prompt, content, req.tags)

    return ChatResponse(
        response=content,
        model=model_name,
        timestamp=datetime.now().isoformat()
    )

# --- Node Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "node": identity.get("node_name", "seed-node")}

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