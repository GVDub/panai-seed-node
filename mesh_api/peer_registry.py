"""
Handles saving, updating, and retrieving peer node information.
"""

import json
from pathlib import Path

NODES_FILE = Path("nodes.json")

def save_peer(data: dict):
    """Save or update peer info in nodes.json"""
    if not NODES_FILE.exists():
        with open(NODES_FILE, "w") as f:
            json.dump([], f)

    with open(NODES_FILE, "r") as f:
        nodes = json.load(f)

    existing = next((n for n in nodes if n["node"] == data["node"]), None)
    if existing:
        existing.update(data)
    else:
        nodes.append(data)

    with open(NODES_FILE, "w") as f:
        json.dump(nodes, f, indent=2)

def load_known_peers() -> list:
    """Load peer info from nodes.json"""
    if not NODES_FILE.exists():
        return []
    with open(NODES_FILE, "r") as f:
        return json.load(f)
