from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseVectorDB(ABC):

    @abstractmethod
    def initialize_collection(self) -> None:
        """Create database tables or collections if they are missing."""
        pass

    @abstractmethod
    def ingest_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Chunk, embed, and permanently write data rows to local storage."""
        pass

    @abstractmethod
    def hybrid_search(self, user_query: str, limit: int = 2) -> List[Dict[str, Any]]:
        """Query the index and return standard dictionaries instead of DB-specific point objects."""
        pass
