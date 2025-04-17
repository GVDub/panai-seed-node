

 # Services Overview
 
 This document provides a high-level summary of the modular service components used in the PanAI Seed Node architecture.
 
 ## Purpose
 
 The PanAI Seed Node is designed to be modular, extensible, and capable of federated AI reasoning. Each service module performs a discrete function that can be developed, tested, and maintained independently. This allows for clearer boundaries of responsibility and facilitates collaborative development.
 
 ## Core Services
 
 ### memory_api
 The `memory_api` service is responsible for logging, retrieving, and reasoning over past memory events. It uses FastAPI and Qdrant for semantic search and long-term recall. This service includes endpoints such as:
 - `/log_memory`
 - `/reflect`
 - `/advise`
 - `/dream`
 - `/plan`
 
 ### config
 The `config` service centralizes application configuration, managing environment-specific settings and toggles for dynamic model routing and inference behavior.
 
 ### logger
 This module sets up standardized logging across services, supporting both console and file output, with optional JSON formatting and timestamping for use in distributed systems.
 
 ### chat
 The `chat` service interfaces with local or remote LLMs (via Ollama or other providers). It handles prompt generation, model selection, and stream or non-stream response options.
 
 ### memory
 This service abstracts memory store interactions, managing the embedding of new data, search queries, and vector database CRUD operations using Qdrant and SentenceTransformers.
 
 ## Integration Path
 
 Each of these modules is imported by the central FastAPI server (`main.py`) and injected via dependency management. This design allows other components (e.g., summarizers, planners, journaling tools) to interface easily with the core services.
 
 ## Future Services
 
 Planned services include:
 - **federation**: secure peer-to-peer memory exchange between nodes
 - **persistence**: long-term archival beyond vector DB
 - **auth**: API authentication and trust mechanisms for federation
 - **metrics**: performance and usage tracking
 
 ---
 For more detailed information on each module, refer to its corresponding documentation page.