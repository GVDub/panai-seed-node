import os

# Qdrant configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "panai_memory")

# Ollama or LLM API configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-nemo")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 60))  # seconds

# Dynamic model selection
ALLOW_DYNAMIC_MODEL_SELECTION = os.getenv("ALLOW_DYNAMIC_MODEL_SELECTION", "true").lower() == "true"
DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", LLM_MODEL)

# Thread settings for embedding models or Ollama (optional)
NUM_THREADS = int(os.getenv("NUM_THREADS", 14))

# Embedding model for SentenceTransformer
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en")

# Federation and inter-node communication
FEDERATION_ENABLED = os.getenv("FEDERATION_ENABLED", "false").lower() == "true"
NODE_ID = os.getenv("NODE_ID", "default-node")
FEDERATION_API_PORT = int(os.getenv("FEDERATION_API_PORT", 8081))
FEDERATION_SECRET = os.getenv("FEDERATION_SECRET", "change-me")

# Model preload options
PRELOAD_MODELS = os.getenv("PRELOAD_MODELS", "true").lower() == "true"

# Embedding configuration
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", 8))

# Vector configuration
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 384))
VECTOR_DISTANCE = os.getenv("VECTOR_DISTANCE", "Cosine")