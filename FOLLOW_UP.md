# 🗺️ Project Checkpoint & Next Steps Run-Book (v1.1.0)

This document serves as an immutable architectural checkpoint file for the **On-Premise Clinical Hybrid RAG Agent & Telemetry Architecture** system state. It maps out the verified working baseline, addresses outstanding core infrastructure issues, and provides direct, executable technical tracks for future development sessions.

---

## 📍 Current Project State Baseline

### 🟩 Fully Operational Components
* **FastAPI Gateway Core:** Running locally on port `8080`. Handles client incoming request loops via the `/api/chat` endpoint natively and smoothly.
* **LangGraph Supervisor Agent:** Running locally via an updated LangChain schema with a native `MemorySaver` checkpointer. Constrained by a strict medical SOAP documentation prompt layout.
* **Polymorphic Dual-Backend Vector Store:** Connects seamlessly via `QdrantClient` and `chroma_backend` architectures to Dockerized instances on ports `6333` and `8000`. Blends dense embeddings (`bge-small-en-v1.5`) and sparse lexical layers (`Splade_PP_en_v1`).

### ⚠️ Outstanding Infrastructure Blockers
* **Inngest Telemetry Handshake Loop:** The background telemetry listener is currently entering an un-finalized `RUNNING` timeout state. This happens because local model initialization and synchronous LLM generation cycles occupy the primary application process, blocking the async event loop from returning the execution completion headers back across the Docker network bridge.

### 📁 Codebase Layout Strategy
The system is currently running in a **unified, high-performance, self-contained monolithic script** inside `main.py` to maintain absolute operational stability and eliminate circular dependency import blocks.

---

## 🛠️ Phase 3 Core Development Tracks

When initializing a new engineering session, choose one of the following isolated development modules to implement:

### 🚀 Immediate Track: Resolving the Inngest Loop Blocker
* **Goal:** Permanently fix the background telemetry loop without altering or blocking your core working agent execution path.
* **Execution Plan:**
  1. Offload the `inngest_client.send` network actions completely out of the hot path of the `/api/chat` endpoint.
  2. Implement a dedicated, multi-process background worker configuration using an isolated `Celery` or `FastAPI BackgroundTasks` queuing system to handle telemetry pings completely separate from the LLM process.
  3. Strip down the `observe_clinical_query` function schema to a terminal, non-returning consumer that drops its execution frame instantly to satisfy the Inngest SDK's tracking lifecycle constraints.

### Tracks A, B, and C
Choose an available pathway to continue expanding system capacity:

#### 🛤️ Track A: Enterprise Architectural Decoupling (Refactoring)
* **Goal:** Split the monolithic `main.py` back into its intended production directory schema (`app/api/routes.py`, `app/core/tasks.py`, `app/database/qdrant_backend.py`) without introducing initialization or configuration errors.

#### 🛤️ Track B: Local RAGAS Mathematical Evaluation Matrix
* **Goal:** Create an autonomous automated evaluation module (`app/core/evaluator.py`) using the open-source **RAGAS framework** powered by a local Ollama `Llama 3.1` critic loop.
* **Metrics to Compute:** Compute mathematical ratios for **Faithfulness** (hallucination checks), **Context Recall** (vector matching performance), and **Answer Relevance** to scientifically score production reliability.

#### 🛤️ Track C: Asynchronous LLM Token Streaming
* **Goal:** Convert the `/api/chat` endpoint from a waiting synchronous block into an active, low-latency typewriter-style stream using FastAPI's `StreamingResponse` and Server-Sent Events (SSE).

---

## 🚀 Phase 4 Advanced Future Enhancements

### 🛤️ Track D: Model Context Protocol (MCP) Integration
* **Goal:** Implement an **MCP Server/Client relationship** within the LangGraph supervisor framework.
* **Utility:** Allows the clinical agent to safely connect to open-standard MCP hosts to read clinical file directories, query local Postgres/SQL databases, or securely pull live research data from external developer tool infrastructures using standard protocols.

### 🛤️ Track E: Advanced Context Engineering & Window Optimization
* **Goal:** Upgrade text chunk ingestion from standard static paragraph splitting to high-fidelity **Parent-Child Chunking** and **Lost-in-the-Middle Context Re-ranking**.
* **Utility:** Maximizes LLM recall performance by splitting text into small child vectors for highly precise mathematical matching, while feeding the full parent context block or a prioritized list of top re-ranked snippets to the local model's attention window.

---

## 🏁 How to Restore the Local Dev Environment

To quickly boot up the entire system from scratch when returning to the workspace, execute these commands across three terminal windows:

### 💻 Terminal 1: Spin up Background Containers
```bash
# Clear out any stale container conflicts
docker rm -f local-inngest

# Start databases and launch Inngest dev server with the host network bridge
docker start local-chroma local-qdrant
docker run -d --net=host --name local-inngest node:18-alpine npx inngest-cli@latest dev -p 8288 -u http://127.0.0
```

### 💻 Terminal 2: Ensure Ollama LLM Runtime is Awake
```bash
ollama run llama3.1
```

### 💻 Terminal 3: Boot Up the Primary Python Application Server
```bash
source .venv/bin/activate
PYTHONPATH=. python main.py
```
