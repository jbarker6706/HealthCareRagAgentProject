from qdrant_client import QdrantClient
from qdrant_client import models
from fastembed.embedding import DefaultEmbedding
from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding
from typing import List, Dict, Any
from app.database.base import BaseVectorDB
from app.config import settings


class QdrantBackend(BaseVectorDB):
    def __init__(self):
        # Fallback to local host routing if specific URL parameters are missing
        qdrant_url = getattr(settings, "QDRANT_URL", "http://localhost:6333")
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = settings.COLLECTION_NAME
        self.dense_model = DefaultEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.sparse_model = SparseTextEmbedding(model_name="prithivida/Splade_PP_en_v1")
        self.initialize_collection()

    def initialize_collection(self) -> None:
        if self.client.collection_exists(collection_name=self.collection_name):
            return
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={"dense-notes": models.VectorParams(size=384, distance=models.Distance.COSINE)},
            sparse_vectors_config={"sparse-notes": models.SparseVectorParams()}
        )

    def ingest_documents(self, chunked_records: List[Dict[str, Any]]) -> None:
        points = []
        for record in chunked_records:
            dense_embeds = list(self.dense_model.embed([record["child_text"]]))[0].tolist()
            sparse_embeds = list(self.sparse_model.embed([record["child_text"]]))[0]

            points.append(
                models.PointStruct(
                    id=record["chunk_id"],
                    vector={
                        "dense-notes": dense_embeds,
                        "sparse-notes": models.SparseVector(
                            indices=sparse_embeds.indices.tolist(),
                            values=sparse_embeds.values.tolist()
                        )
                    },
                    payload={
                        "parent_id": record["parent_id"],
                        "clinical_note": record["parent_context"],
                        **record["metadata"]
                    }
                )
            )
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

    def hybrid_search(self, user_query: str, limit: int = 1) -> List[Dict[str, Any]]:
        query_dense = list(self.dense_model.embed([user_query]))[0].tolist()
        query_sparse_raw = list(self.sparse_model.embed([user_query]))[0]

        query_sparse = models.SparseVector(
            indices=query_sparse_raw.indices.tolist(),
            values=query_sparse_raw.values.tolist()
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                models.Prefetch(query=query_dense, using="dense-notes", limit=limit),
                models.Prefetch(query=query_sparse, using="sparse-notes", limit=limit),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit
        )

        standardized_hits = []
        if results and hasattr(results, 'points') and results.points:
            for hit in results.points:
                payload = hit.payload if hit.payload is not None else {}
                standardized_hits.append({
                    "patient_id": payload.get("patient_id", "Unknown Patient"),
                    "text": payload.get("clinical_note", "No text context parsed.")
                })
        return standardized_hits
