 # Optimization Strategies for PanAI Edge Inference
 
 This document outlines current and proposed strategies for improving performance and responsiveness when running PanAI’s memory and inference systems on edge-class devices like the Aoostar GEM 10.
 
 ## CPU Thread Management
 
 - Set environment variables before launching inference services:
   ```bash
   export OMP_NUM_THREADS=14
   export MKL_NUM_THREADS=14
   ```
 - Within Python:
   ```python
   import torch
   torch.set_num_threads(14)
   ```
 
 ## FastAPI Server Scaling
 
 - Run the FastAPI app with multiple workers:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```
 
 ## Model Management & Preloading
 
 - Import model loading from `model_manager`:
   ```python
   from model_manager import load_model
   ```
 - Preload both lightweight and heavyweight models at server start if RAM permits:
   ```python
   mistral_model = load_model('mistral')
   mistral_nemo_model = load_model('mistral-nemo')
   ```
 - For constrained RAM, use lazy loading and caching:
   ```python
   if not loaded_models.get("mistral"):
       loaded_models["mistral"] = load_model("mistral")
   ```
 
 ## Ollama/Open WebUI Integration

 - If using Ollama outside of Docker, ensure containers can reach it via `host.docker.internal` or a `.env`-defined URL.
 - Use `OLLAMA_BASE_URL` in `.env` to define model access point across environments.
 - Open WebUI containers may need to be restarted with `docker compose down && docker compose up -d` to recognize changes.
 
 ## Quantization & Model Selection
 
 - Favor quantized models like `Q4_0` or `Q4_K_M` to reduce load and memory usage.
 
 ## CPU Scaling Governor
 
 - Set governor to `performance` on Linux:
   ```bash
   sudo cpupower frequency-set -g performance
   ```
 
 ## Request Batching
 
 - Optimize memory log retrieval and LLM prompt generation with batched queries when appropriate.
 
 ## System Monitoring
 
 - Monitor performance in real-time with:
   ```bash
   htop     # CPU/Memory
   iotop    # Disk I/O
   glances  # Overall system
   ```
 
 ## Additional Tips
 
 - Leave 1–2 CPU threads free for system overhead to prevent slowdowns.
 - Profile using representative workloads before scaling.
 - Use `journalctl -u panai-memory -f` or `docker logs -f <container>` to monitor real-time application logs.
 
 ---
 Last updated: 2025-05-01
 