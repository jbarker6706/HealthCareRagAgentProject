import uuid
from typing import List, Dict, Any


class ParentChildProcessor:
    def __init__(self, parent_size: int = 1000, child_size: int = 200, overlap: int = 50):
        self.parent_size = parent_size
        self.child_size = child_size
        self.overlap = overlap

    def process_note(self, clinical_note: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits a document into linked Parent and Child chunks for indexing."""
        processed_chunks = []
        note_length = len(clinical_note)

        # Slide through text creating Parent blocks
        for i in range(0, note_length, self.parent_size - self.overlap):
            parent_text = clinical_note[i: i + self.parent_size]
            parent_id = str(uuid.uuid4())

            # Split this specific parent down into smaller child blocks
            for j in range(0, len(parent_text), self.child_size - self.overlap):
                child_text = parent_text[j: j + self.child_size]

                chunk_record = {
                    "chunk_id": str(uuid.uuid4()),
                    "parent_id": parent_id,
                    "child_text": child_text,
                    "parent_context": parent_text,
                    "metadata": {
                        **metadata,
                        "is_child": True
                    }
                }
                processed_chunks.append(chunk_record)

        return processed_chunks


text_processor = ParentChildProcessor()
