# Deployment

This document outlines the steps to deploy a PanAI Seed Node instance, either in standalone mode or as part of a federated local network.

## Prerequisites

- A system with at least 16GB RAM and SSD/NVMe storage
- Docker and Docker Compose installed
- Python 3.10 or later with `venv` support
- Git for cloning the repository

## Step-by-Step Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/GVDub/panai-seed-node.git
cd panai-seed-node
```

### 2. Configure the Environment

Copy the `.env.example` file to `.env` and fill in the necessary values:

```bash
cp .env.example .env
```

Adjust ports, model paths, or API keys as needed for your local setup.

### 3. Set Up the Memory Subsystem

Create and activate a virtual environment, then install requirements:

```bash
cd panai-memory
python -m venv venv
source panai-memory/bin/activate
pip install -r requirements.txt
```

### 4. Launch Vector Database and UI

From the project root or `open-webui` directory:

```bash
docker compose up -d
```

Ensure volumes are properly bound to your desired storage directories (see `docker-compose.yml`).

**Note:** The `.env` variables are now used to configure Open WebUI and should be reviewed carefully, especially if deploying across different operating system environments.

### 5. Run the Memory API Server

In a separate terminal:

```bash
cd panai-memory
source panai-memory/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Optional: Federated Deployment

See [`federation.md`](./federation.md) for details on setting up trusted peer communication between nodes.

## Monitoring

You may wish to add Watchtower or other update-monitoring tools to ensure containers stay current.

## Persistence

Ensure your data volumes (Qdrant, memory logs, reflections) are mapped to persistent storage and backed up regularly.

## Next Steps

- Configure API access controls (see `security.md`)
- Explore the memory subsystem’s capabilities via Swagger UI
- Add journaling, reflection, and planning extensions to expand contextual awareness
- Familiarize yourself with the modular code structure introduced in version 0.3.0+ (see development.md)
