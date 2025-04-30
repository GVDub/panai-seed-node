import os
from datetime import datetime
from memory_api.memory_api import MemoryEntry, log_memory as async_log_memory
import logging
import asyncio

logger = logging.getLogger(__name__)

def log_interaction(prompt, response, tags, access, model_name):
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
    os.makedirs("audit_log", exist_ok=True)
    with open(log_file, "a") as f:
        f.write(log_entry)

    # Also log to memory system
    try:
        memory_entry = MemoryEntry(
            text=f"**Prompt:** {prompt}\n\n**Response:** {response}",
            session_id=f"chat-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            tags=tags + ["chat", "shared"]
        )
        asyncio.create_task(async_log_memory(memory_entry))
    except Exception as e:
        logger.warning(f"[Audit] Failed to log memory from chat: {e}")

__all__ = ["log_interaction"]