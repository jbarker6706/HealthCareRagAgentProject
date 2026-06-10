# from app.config import settings
# from app.database.qdrant_backend import QdrantBackend
# # from app.database.chroma_backend import ChromaBackend
#
# def get_vector_db():
#     """Polymorphic database resolver factory."""
#     if settings.VECTOR_DB_BACKEND.lower() == "qdrant":
#         print("💡 Polymorphic Resolver: Initializing Qdrant Hybrid Engine")
#         return QdrantBackend()
#     # elif settings.VECTOR_DB_BACKEND.lower() == "chroma":
#     #     print("💡 Polymorphic Resolver: Initializing Chroma Semantic Engine")
#     #     return ChromaBackend()
#     else:
#         raise ValueError(f"Unsupported database backend: {settings.VECTOR_DB_BACKEND}")
def get_vector_db():
    """Polymorphic database resolver factory (Temporarily isolated to Qdrant)."""
    from app.config import settings
    from app.database.qdrant_backend import QdrantBackend

    if settings.VECTOR_DB_BACKEND.lower() == "qdrant":
        print("💡 Polymorphic Resolver: Initializing Qdrant Hybrid Engine")
        return QdrantBackend()
    else:
        raise ValueError(
            f"Database '{settings.VECTOR_DB_BACKEND}' is temporarily disabled. "
            "Please set VECTOR_DB_BACKEND = 'qdrant' in app/config.py"
        )
