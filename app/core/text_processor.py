import uuid


class TextProcessor:
    def process_note(self, text: str, metadata: dict) -> list:
        """
        Splits text into chunks using an advanced parent-child strategy.
        Outputs exact dictionary fields required by QdrantBackend.
        """
        # Generate a unified ID for the full original note (The Parent)
        parent_id = str(uuid.uuid4())

        # Split text into smaller semantic sentences/chunks (The Children)
        child_chunks = [c.strip() for c in text.split(". ") if c.strip()]
        records = []

        for idx, child_text in enumerate(child_chunks):
            records.append({
                "chunk_id": str(uuid.uuid4()),  # Generates a clean UUID compliant with PointStruct requirements
                "child_text": child_text,
                "parent_id": parent_id,
                "parent_context": text,  # Keeps the full original note context intact
                "metadata": metadata
            })
        return records


text_processor = TextProcessor()
