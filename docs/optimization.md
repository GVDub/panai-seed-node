

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
   uvicorn memory_api:app --host 0.0.0.0 --port 8000 --workers 4
   ```
 
 ## Model Management & Preloading
 
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
 
 ## Model Warmup
 
 - After loading, run a dummy prompt to warm up:
   ```python
   model("What is 2 + 2?")
   ```
 
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
 
 ---
 Last updated: 2025-04-18