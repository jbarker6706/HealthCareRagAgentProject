# 🗺️ Project Checkpoint & Next Steps Run-Book (v1.1.0)

This document serves as an immutable architectural checkpoint file for the **On-Premise Clinical Hybrid RAG Agent & Telemetry Architecture** system state. It maps out the verified working baseline and provides direct, executable technical tracks for future development sessions.

---

## 📍 Current Project State Baseline

### 🟩 Fully Operational Components
* **FastAPI Gateway Core:** Running locally on port `8080`. Handles synchronous client incoming request loops via the `/api/chat` endpoint.
* **LangGraph Supervisor Agent:** Running locally via an updated LangChain schema with a native `MemorySaver` checkpointer. Constrained by a strict medical SOAP documentation prompt layout.
* **Polymorphic Dual-Backend Vector Store:** Connects seamlessly via `QdrantClient` and `chroma_backend` architectures to Dockerized instances on ports `6333` and `8000`. Blends dense embeddings (`bge-small-en-v1.5`) and sparse lexical layers (`Splade_PP_en_v1`).
* **Inngest Telemetry Pipeline:** Executes inside an Alpine Docker container configured with host networking (`--net=host`). Handshakes automatically with FastAPI on port `8080/api/inngest` via a Pydantic-validated `TriggerEvent` constructor tracking the `clinical/query.requested` trace.

### 📁 Codebase Layout Strategy
The system is currently running in a **unified, high-performance, self-contained monolithic script** inside `main.py` to maintain operational stability and eliminate circular dependency import blocks.

---

## 🛠️ Phase 3 Core Development Tracks

When initializing a new engineering session, choose one of the following isolated development modules to implement:

### 🛤️ Track A: Enterprise Architectural Decoupling (Refactoring)
* **Goal:** Split the monolithic `main.py` back into its intended production directory schema (`app/api/routes.py`, `app/core/tasks.py`, `app/database/qdrant_backend.py`) without introducing initialization or configuration errors.

### 🛤️ Track B: Local RAGAS Mathematical Evaluation Matrix
* **Goal:** Create an autonomous automated evaluation module (`app/core/evaluator.py`) using the open-source **RAGAS framework** powered by a local Ollama `Llama 3.1` critic loop.
* **Metrics to Compute:** Compute mathematical ratios for **Faithfulness** (hallucination checks), **Context Recall** (vector matching performance), and **Answer Relevance** to scientifically score production reliability.

### 🛤️ Track C: Asynchronous LLM Token Streaming
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

# Start databases and launch Inngest dev server with the exact fully qualified FastAPI URL
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
