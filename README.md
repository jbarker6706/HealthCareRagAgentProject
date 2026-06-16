# 🏥 On-Premise Clinical Hybrid RAG Agent & Patient Record Architecture (v2.0.0)

An enterprise-grade, 100% local, air-gapped Artificial Intelligence system engineered to process massive multi-page electronic health records (EHR), unstructured clinical notation logs, and global medical research literature. Completely refactored from a monolithic prototype into a decoupled, production-ready polymorphic architecture, this platform guarantees absolute data sovereignty and strict HIPAA compliance boundaries by executing exclusively on-premise.

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
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │    Supervisor Agent       │
                         │  (app/core/agent_graph.py)│
                         └─────────────┬─────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
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
* **Qdrant Hybrid Engine Engine (`qdrant_backend.py`):** Combines dense semantic vectors (`bge-small-en-v1.5`) with sparse lexical tokens (`Splade_PP_en_v1`) processed through Reciprocal Rank Fusion (RRF).
* **Chroma Semantic Engine (`chroma_backend.py`):** Runs an ultra-lightweight, local, disk-backed persistent semantic document cluster utilizing optimized FastEmbed float extractions.

### 2. Context Engineering & Programmatic HIPAA Security
* **Parent-Child Chunk Partitioning (`text_processor.py`):** Mitigates LLM context window clutter. Documents are split into precise 200-character tokens (children) for vector matching, but link back to 1000-character paragraphs (parents) to supply the LLM with ample diagnostic data.
* **HIPAA Compliance Redactor (`phi_sanitizer.py`):** A rigid security interception layer that applies compiled regular expressions to strip out Protected Health Information (PHI) like SSNs, Medical Record Numbers (MRN), phone numbers, and emails before ingestion.

---

## 🛠️ Modular Directory Layout

```text
HealthCareRagAgentProject/
│
├── data/raw/synthetic.csv          # Local EHR patient text rows (Git-ignored)
├── app/
│   ├── __init__.py                 # Namespace declaration package
│   ├── config.py                   # Centralized Pydantic application parameters
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py               # FastAPI high-performance query endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── phi_sanitizer.py        # Regex HIPAA security interceptor
│   │   ├── text_processor.py       # Sliding-window parent-child chunk engine
│   │   └── agent_graph.py          # LangGraph Supervisor multi-agent core
│   └── database/
│       ├── __init__.py             # Dynamic get_vector_db factory resolver
│       ├── base.py                 # Abstract Polymorphic Base Interface Class
│       ├── qdrant_backend.py       # Sparse/Dense hybrid search implementation
│       └── chroma_backend.py       # Disk-persistent dense matching engine
│
├── main.py                         # Unified system gateway startup script
├── test_rag.py                     # Isolation and infrastructure test harness
└── README.md                       # Professional portfolio documentation
```

---

## ⚡ Technical Talking Points for Recruiters

* **Decoupled Interface-Driven Design:** "I engineered the data layer around an abstract class layout. This polymorphism allows enterprise systems to switch their data persistence store from a lightweight cluster like Chroma to an advanced hybrid store like Qdrant instantly via configuration strings."
* **Data Sovereignty & Zero Variable Costs:** "This architecture runs 100% locally. Zero bytes of sensitive data leave the infrastructure boundaries, aligning with strict HIPAA guardrails and avoiding volatile API token pricing networks."
* **Advanced Context Engineering:** "By splitting documents into minor children shards for crisp mathematical matching while passing parent paragraphs to the local `Llama 3.1` model, the system maintains high recall while eliminating hallucinations."

---

## 🏁 Verification & Subsystem Execution

### 1. Run the Isolation Test Harness
Validate either vector store engine instantly by calling the test runner tool with inline variables:
```bash
# Evaluate Qdrant hybrid extraction
VECTOR_DB_BACKEND=qdrant PYTHONPATH=. python test_rag.py

# Evaluate Chroma dense persistence mapping
VECTOR_DB_BACKEND=chroma PYTHONPATH=. python test_rag.py
```

### 2. Launch the Production FastAPI Framework Backend Server
Set your configuration option inside `app/config.py` and boot the server application endpoint:
```bash
PYTHONPATH=. python main.py
```
*The service instantly listens for client requests at: **`http://127.0.0.1:8080`***
