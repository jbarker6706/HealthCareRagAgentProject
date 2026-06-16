import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Healthcare Patient Record Agent & RAG System"

    # Selected Database ("qdrant" or "chroma")
    # This fulfills your polymorphic requirement
    VECTOR_DB_BACKEND: str = "chroma"

    # Infrastructure Endpoints
    QDRANT_URL: str = "http://localhost:6333"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.1"

    # Collection Specs
    COLLECTION_NAME: str = "asclepius_clinical_notes"

    class Config:
        case_sensitive = True


settings = Settings()
