# model_manager/model_manager.py

import requests
import json
import os
from datetime import datetime, timedelta

# Load NODE_NAME from config.json
CONFIG_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

try:
    with open(CONFIG_JSON_PATH, "r") as f:
        config = json.load(f)
        NODE_NAME = config.get("node_name", "unknown-node")
except Exception as e:
    log(f"[ModelManager] Warning: Failed to load node name from config.json: {e}", level="WARNING")
    NODE_NAME = "unknown-node"

# Constants
OLLAMA_HOST = "http://localhost:11434"
MODELS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "models.json")

# Cache variables
models_available = []
last_refresh = None
REFRESH_INTERVAL = timedelta(days=1)  # Refresh once per day

def load_models_from_ollama():
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags")
        response.raise_for_status()
        models_info = response.json().get('models', [])

        models = []
        for model in models_info:
            models.append(model['model'])

        return models

    except requests.RequestException as e:
        log(f"[ModelManager] Warning: Ollama unavailable ({e}). Falling back to models.json.", level="WARNING")
        return None

def load_models_from_json():
    try:
        with open(MODELS_JSON_PATH, "r") as f:
            data = json.load(f)
            return data.get("models", [])
    except Exception as e:
        log(f"[ModelManager] Error loading models.json: {e}", level="WARNING")
        return []

def get_available_models(force_refresh=False):
    global models_available, last_refresh

    now = datetime.now()

    if force_refresh or last_refresh is None or (now - last_refresh) > REFRESH_INTERVAL:
        log("[ModelManager] Refreshing model list...", level="INFO")
        models = load_models_from_ollama()
        if models:
            models_available = models
            try:
                with open(MODELS_JSON_PATH, "w") as f:
                    json.dump({
                        "node_name": NODE_NAME,
                        "models": models_available
                    }, f, indent=2)
                log("[ModelManager] models.json updated successfully.", level="INFO")
            except Exception as e:
                log(f"[ModelManager] Warning: Failed to update models.json: {e}", level="WARNING")
        else:
            models_available = load_models_from_json()

        last_refresh = now
    else:
        pass  # Within refresh window; use cached list

    return models_available