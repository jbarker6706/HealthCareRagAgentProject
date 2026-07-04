# 🏥 On-Premise Clinical Hybrid RAG Agent & Telemetry Architecture (v2.1.0)

An enterprise-grade, 100% local, air-gapped Artificial Intelligence platform engineered to process unstructured clinical notation logs and electronic health records (EHR) with strict data sovereignty. This system is designed around an interface-driven polymorphic data core, managed by a LangGraph State engine, and audited via an isolated background telemetry framework.

---

## 🚀 Core Architecture Overview

This decoupled platform routes client interactions through a high-performance web API framework, leveraging state-machine routing loops and an interchangeable data retention layer.

```text
               [ Clinician User Client Request via HTTP / REST ]
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   FastAPI Gateway Router  │
                         │     (app/api/routes.py)   │
                         │        (Port 8080)        │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │    Supervisor Agent       │
                         │  (app/core/agent_graph.py)│
                         └─────────────┬─────────────┘
                                       ├──────────────────────────────┐
                                       ▼ (Sync Pipeline)              ▼ (OS-Level Detached Thread)
                         ┌───────────────────────────┐  ┌───────────────────────────┐
                         │    Supervisor Agent       │  │   Inngest Dev Telemetry   │
                         │    (LangGraph Engine)     │  │     (Port 8288 Host)      │
                         └─────────────┬─────────────┘  └───────────────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
                ▼ (Polymorphic Driver Selection)              ▼ 
   ┌────────────────────────┐                    ┌────────────────────────┐
   │   EMR Retrieval RAG    │                    │  Clinical Trial Agent  │
   │  (Polymorphic Interface)│                    │   (Web Search Tool)    │
   └────────────┬───────────┘                    └────────────────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
┌──────────────┐┌──────────────┐
│  Qdrant DB   ││  Chroma DB   │
│(Hybrid Search)│(Dense Vector)│
└──────────────┘└──────────────┘
```

### 1. Polymorphic Multi-Backend Vector Core
The system features an abstract database implementation layer (`app/database/base.py`) that permits switching the underlying hardware storage engine dynamically at boot time via configurations without modifying upstream code components:
* **Qdrant Hybrid Engine (`qdrant_backend.py`):** Combines dense semantic vectors (`bge-small-en-v1.5`) with sparse lexical tokens (`Splade_PP_en_v1`) processed through Reciprocal Rank Fusion (RRF).
* **Chroma Semantic Engine (`chroma_backend.py`):** Runs an ultra-lightweight, local, disk-backed persistent semantic document cluster utilizing optimized FastEmbed float extractions.

### 2. Thread-Isolated Auditing & Telemetry
To bypass event-loop starvation caused by heavy local LLM inference models, the system completely untethers tracing and security compliance logging from the primary process. Telemetry triggers are dispatched onto an independent OS-level background thread, sending immediate `200 OK` responses back to clinicians while logging trails concurrently.

### 3. Context Engineering & Programmatic HIPAA Security
* **Parent-Child Chunk Partitioning:** Mitigates LLM context window clutter. Documents are split into precise 200-character tokens (children) for vector matching, but link back to 1000-character paragraphs (parents) to supply the LLM with ample diagnostic data.
* **HIPAA Compliance Redactor:** A rigid security interception layer that applies compiled regular expressions to strip out Protected Health Information (PHI) like SSNs, Medical Record Numbers (MRN), phone numbers, and emails before ingestion.

---

## ⚡ Technical Talking Points for Recruiters

* **Polymorphic Database Decoupling:** "I engineered an abstract, dual-backend data model. By running Chroma and Qdrant in separate containers, the application can serve lightweight persistent lookups or execute complex hybrid search queries blending dense semantics and sparse token structures using Reciprocal Rank Fusion."
* **Hardware Thread-Separated Architecture:** "To maintain rapid HTTP response loops under heavy local inference, I offloaded Inngest telemetry logging to dedicated OS-level threads. This frees up the shared event loop from CPU-bound locks during Llama generation blocks, preventing networking delays across our Docker bridge."
* **Persistent Local Vector Storage:** "By establishing Docker mounts mapping to local machine directories, vector indices persist across runtime container lifecycles, completely bypassing expensive cloud synchronization architectures."

---

## 🏁 Verification & Subsystem Execution

### 1. Initialize Persistent Local Containers & Telemetry Server
```bash
# A. Start the Dockerized Chroma Persistent Database
docker run -d -p 8000:8000 \
  -v \$(pwd)/chroma_storage:/chroma/data \
  --name local-chroma \
  chromadb/chroma

# B. Start the Dockerized Qdrant Hybrid Cluster
docker run -d -p 6333:6333 -p 6334:6334 \
  -v \$(pwd)/qdrant_storage:/qdrant/storage \
  --name local-qdrant \
  qdrant/qdrant

# C. Start the Inngest Telemetry Server via Host Networking Interface
docker rm -f local-inngest
docker run -d --net=host --name local-inngest node:18-alpine npx inngest-cli@latest dev -p 8288 -u http://127.0.0.1:8080/api/inngest
```

### 2. Launch the Application Server
```bash
source .venv/bin/activate
INNGEST_DEV=1 PYTHONPATH=. python main.py
```
