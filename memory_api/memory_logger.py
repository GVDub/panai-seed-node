import os
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import asyncio


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler for WARNING and above
error_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "panai-error.log"), maxBytes=2_000_000, backupCount=3
)
error_handler.setLevel(logging.WARNING)
error_handler.setFormatter(formatter)
logger.addHandler(error_handler)

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

def log_ops_event(message: str, level: str = "INFO"):
    log_path = os.path.join(LOG_DIR, "panai-ops.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} [{level.upper()}] {message}\n"
    with open(log_path, "a") as log_file:
        log_file.write(entry)

def log_shutdown_event(message: str = "Shutdown initiated"):
    log_ops_event(message)

__all__ = ["log_interaction", "logger", "log_ops_event", "log_shutdown_event"]