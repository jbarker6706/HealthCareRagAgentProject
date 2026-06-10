def get_vector_db():
    """Polymorphic database resolver factory (Fully Functional Qdrant & Chroma)."""
    from app.config import settings
    from app.database.qdrant_backend import QdrantBackend
    from app.database.chroma_backend import ChromaBackend

    if settings.VECTOR_DB_BACKEND.lower() == "qdrant":
        print("💡 Polymorphic Resolver: Initializing Qdrant Hybrid Engine")
        return QdrantBackend()
    elif settings.VECTOR_DB_BACKEND.lower() == "chroma":
        print("💡 Polymorphic Resolver: Initializing Chroma Semantic Engine")
        return ChromaBackend()
    else:
        raise ValueError(f"Unsupported database backend: {settings.VECTOR_DB_BACKEND}")
