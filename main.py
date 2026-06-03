
import os
import uuid
import pandas as pd
import gradio as gr

from qdrant_client import QdrantClient
from qdrant_client import models  # Essential for Prefetch, Distance, etc.
from fastembed.embedding import DefaultEmbedding
from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding

# MODERN PRODUCTION LANGCHAIN V1.0 STRUCTURE
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.chat_history import InMemoryChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory


# ==========================================================
# 1. GLOBAL INITIALIZATION & LOCAL MODELS
# ==========================================================
client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "asclepius_clinical_notes"

print("Initializing local embedding models globally...")
dense_model = DefaultEmbedding(model_name="BAAI/bge-small-en-v1.5")
sparse_model = SparseTextEmbedding(model_name="prithivida/Splade_PP_en_v1")


# ==========================================================
# 2. FIXED HYBRID SEARCH ENGINE
# ==========================================================
def hybrid_query_engine(user_query: str, limit: int = 2):
    # 1. Safely extract raw nested embedding list values
    query_dense = list(dense_model.embed([user_query]))[0].tolist()

    # 2. Extract and structure the sparse weights matrix matrix
    query_sparse_raw = list(sparse_model.embed([user_query]))[0]
    query_sparse = models.SparseVector(
        indices=query_sparse_raw.indices.tolist(),
        values=query_sparse_raw.values.tolist()
    )

    # 3. FIX: Execute Qdrant universal hybrid query using FusionQuery engine
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            models.Prefetch(query=query_dense, using="dense-notes", limit=limit),
            models.Prefetch(query=query_sparse, using="sparse-notes", limit=limit),
        ],
        query=models.FusionQuery(
            fusion=models.Fusion.RRF  # Resolves 'AttributeError: rrf' natively
        ),
        limit=limit
    )
    return results


# ==========================================================
# 3. DATA VECTOR PERSISTENCE MANAGING
# ==========================================================
if client.collection_exists(collection_name=COLLECTION_NAME):
    collection_info = client.get_collection(collection_name=COLLECTION_NAME)
    should_embed_data = collection_info.points_count == 0
else:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={"dense-notes": models.VectorParams(size=384, distance=models.Distance.COSINE)},
        sparse_vectors_config={"sparse-notes": models.SparseVectorParams()}
    )
    should_embed_data = True

if should_embed_data:
    csv_file_path = "data/raw/synthetic.csv"
    print(f"Processing database initialization from {csv_file_path}...")
    df = pd.read_csv(csv_file_path)
    points = []

    for index, row in df.iterrows():
        clinical_note = str(row['note'])
        patient_id = row.get('patient_id', f"PATIENT_{index}")

        dense_embeds = list(dense_model.embed([clinical_note]))[0].tolist()
        sparse_embeds = list(sparse_model.embed([clinical_note]))[0]

        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector={
                    "dense-notes": dense_embeds,
                    "sparse-notes": models.SparseVector(
                        indices=sparse_embeds.indices.tolist(),
                        values=sparse_embeds.values.tolist()
                    )
                },
                payload={"patient_id": patient_id, "clinical_note": clinical_note, **row.to_dict()}
            )
        )

        if len(points) >= 25:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            points = []

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("Database indexing complete.")


# ==========================================================
# 4. AGENT RAG TOOLS & MEMORY PIPELINE (LangChain 1.0+)
# ==========================================================
@tool
def query_patient_records(patient_name: str, query: str) -> str:
    """Look up a specific patient's local medical charts, history, and lab results."""
    search_query = f"Patient {patient_name}: {query}"
    try:
        search_hits = hybrid_query_engine(search_query, limit=2)
    except Exception as e:
        return f"Error querying local vector database: {str(e)}"

    if not search_hits.points:
        return f"No medical records found matching '{search_query}'."

    context_blocks = [f"-[ID: {h.payload.get('patient_id')}]-\n{h.payload.get('clinical_note')}" for h in
                      search_hits.points]
    return "\nFound clinical notes:\n" + "\n".join(context_blocks)


@tool
def search_medical_guidelines(medical_term: str) -> str:
    """Search public medical literature, drug databases, and clinical guidelines."""
    return f"Mock Web Result: Standard treatment for {medical_term} includes lifestyle modifications."


# Strict System Prompt Layout enforcing SOAP documentation structures
CLINICAL_SYSTEM_PROMPT = """You are a precise AI Healthcare Assistant running in a secure vector RAG database.

When responding to user requests about specific records, you MUST map out your response inside a standardized medical SOAP block:
1. **SUBJECTIVE**: Document chief complaints, timeline, and history statements provided by the patient records.
2. **OBJECTIVE**: Explicitly list vital signs, lab metrics, or direct doctor examinations found.
3. **ASSESSMENT**: Provide an evaluation synthesis, active diagnostic problems, or clinical impressions.
4. **PLAN**: Map therapeutic paths, medications, follow-up instructions, or diagnostic next steps.

Rules:
- Rely strictly on extracted database facts. Do not invent context.
- Keep observations direct, factual, and brief."""

llm = ChatOllama(model="llama3.1", temperature=0, base_url="http://localhost:11434")
tools = [query_patient_records, search_medical_guidelines]

# 1. Initialize LangGraph's native memory saver
memory_checkpointer = MemorySaver()

# 2. Compile the agent directly with the native checkpointer
# This removes the need for RunnableWithMessageHistory entirely
agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=CLINICAL_SYSTEM_PROMPT,
    checkpointer=memory_checkpointer
)


# ==========================================================
# 5. GRADIO INTERACTIVE OPEN-SOURCE WEB UI
# ==========================================================
def gradio_chat_interface(message, history):
    """
    Handles user text queries using modern LangChain V1.0 structures.
    Gradio automatically manages message state values inside history payloads.
    """
    # 1. Extract the raw string query text safely from the Gradio input
    if isinstance(message, dict) and "text" in message:
        user_query = message["text"]
    elif hasattr(message, "text"):
        user_query = message.text
    else:
        user_query = str(message)

    # 2. Map a unique thread identifier for LangGraph state checkpoint persistence
    config = {"configurable": {"thread_id": "gradio_local_session"}}

    # 3. Format inputs using standard text mapping.
    inputs = {"messages": user_query}

    try:
        # 4. Invoke your compiled agent graph execution engine
        result = agent_executor.invoke(inputs, config=config)

        # 5. Safely pull out the final assistant response string text payload
        agent_response = result["messages"][-1].content
        return agent_response

    except Exception as e:
        return f"⚠️ System Processing Error: {str(e)}"


# ==========================================================
# 6. RUN ENGINE PIPELINES & VISUAL LAUNCH
# ==========================================================
if __name__ == "__main__":
    print("\n--- Running Hybrid Search API Isolation check ---")
    test_query = "Patients diagnosed with CAD showing signs of respiratory distress"
    try:
        search_hits = hybrid_query_engine(test_query)
        print(f"Extraction operational. Found {len(search_hits.points)} top matches.")
    except Exception as e:
        print(f"Database search isolation warning: {e}")

    print("\n🚀 Starting Open-Source Clinical Web Dashboard...")

    # FIX: Removed 'theme="soft"' to prevent the Gradio TypeError completely
    demo = gr.ChatInterface(
        fn=gradio_chat_interface,
        title="🏥 Open-Source Clinical Hybrid RAG Agent",
        description="Powered locally by Ollama (Llama 3.1), Qdrant Hybrid Vector DB, and LangGraph State Memory."
    )

    # Launch the application interface server locally at http://127.0.0.1:7860
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
