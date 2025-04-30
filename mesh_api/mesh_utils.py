"""
Utility functions for peer mesh operations, such as normalization,
deduplication, and shared helpers used across the mesh layer.
"""

import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("mesh_chat_log.json")

def log_chat_to_mesh(data: dict):
    """Append a timestamped chat exchange from a peer to the shared mesh log."""
    timestamped_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "peer": data.get("peer", "unknown"),
        "content": data.get("content", "")
    }

    logs = []
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(timestamped_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
