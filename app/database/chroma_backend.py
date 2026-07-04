import chromadb
from fastembed.embedding import DefaultEmbedding
from typing import List, Dict, Any
from app.database.base import BaseVectorDB
from app.config import settings

class ChromaBackend(BaseVectorDB):
    def __init__(self):
        # Explicit HTTP client mapping to the local-chroma Docker container
        self.client = chromadb.HttpClient(host="localhost", port=8000)
        self.dense_model = DefaultEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.collection_name = settings.COLLECTION_NAME
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def initialize_collection(self) -> None:
        pass

    def ingest_documents(self, chunked_records: List[Dict[str, Any]]) -> None:
        ids, embeddings, documents, metadatas = [], [], [], []

        for record in chunked_records:
            dense_embeds = list(self.dense_model.embed([record["child_text"]]))[0].tolist()
            ids.append(record["chunk_id"])
            embeddings.append(dense_embeds)
            documents.append(record["parent_context"])
            metadatas.append({
                "patient_id": str(record["metadata"].get("patient_id", "Unknown")),
                "parent_id": record["parent_id"]
            })

        if ids:
            self.collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    def hybrid_search(self, user_query: str, limit: int = 1) -> List[Dict[str, Any]]:
        query_dense = list(self.dense_model.embed([user_query]))[0].tolist()
        results = self.collection.query(query_embeddings=[query_dense], n_results=limit)

        standardized_hits = []
        if results and results.get("documents") and results["documents"]:
            for docs, metas in zip(results["documents"], results["metadatas"]):
                for doc, meta in zip(docs, metas):
                    standardized_hits.append({
                        "patient_id": meta.get("patient_id", "Unknown Patient"),
                        "text": doc if doc is not None else "No text context parsed."
                    })
        return standardized_hits
