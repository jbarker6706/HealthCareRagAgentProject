import os
import sys

# 1. Force check the path environment
print("--- Python Path Debug ---")
print("Current Working Directory:", os.getcwd())
print("System Search Paths:")
for path in sys.path[:3]:
    print(f" - {path}")

# 2. Hard inspect the database directory layout
db_dir = os.path.join(os.getcwd(), "app", "database")
print(f"\nInspecting Database Directory: {db_dir}")
if os.path.exists(db_dir):
    print("Files found in folder:", os.listdir(db_dir))
else:
    print("❌ ERROR: The path 'app/database' does not physically exist relative to your terminal context!")
print("-------------------------\n")

# Framework and modular engine imports
import pandas as pd
from app.config import settings
from app.database import get_vector_db
from app.core.phi_sanitizer import phi_sanitizer
from app.core.text_processor import text_processor


def run_rag_validation():
    print("🚀 Starting Local RAG Subsystem Validation Test...")

    # 1. Initialize the Polymorphic Database Backend
    try:
        db = get_vector_db()
        db.initialize_collection()
        print("✅ Database backend initialized and collection prepared.")
    except Exception as e:
        print(f"❌ Initialization Failed: {str(e)}")
        return

    # 2. Verify dataset path layout
    csv_file_path = "data/raw/synthetic.csv"
    if not os.path.exists(csv_file_path):
        print(f"❌ Error: Could not find raw file at {csv_file_path}")
        return

    print(f"Reading sample rows from local dataset...")
    df = pd.read_csv(csv_file_path).head(3)  # Parse first 3 rows for speed

    chunked_records = []
    for index, row in df.iterrows():
        raw_note = str(row['note'])
        p_id = row.get('patient_id', f"PATIENT_{index}")

        # 3. Apply HIPAA PHI Redaction programmatically
        sanitized_note = phi_sanitizer.redact(raw_note)

        # 4. Generate Parent-Child chunk dictionaries
        metadata = {"patient_id": p_id, "original_index": index}
        records = text_processor.process_note(sanitized_note, metadata=metadata)
        chunked_records.extend(records)

    print(f"Extracted {len(chunked_records)} parent-child chunks. Writing to vector DB...")

    try:
        db.ingest_documents(chunked_records)
        print("✅ Ingestion pipeline test successful.")
    except Exception as e:
        print(f"❌ Ingestion Failed: {str(e)}")
        return

    # 5. Run a Test Query using the unified polymorphic interface search method
    test_query = "Check for historical logs regarding chest distress or CAD"
    print(f"\nTesting hybrid search with query: '{test_query}'...")

    try:
        results = db.hybrid_search(test_query, limit=1)
        print(f"✅ Search API executed successfully. Found {len(results)} hit(s).")

        for idx, hit in enumerate(results):
            print(f"\n--- [Matched Hit #{idx + 1}] ---")
            print(f"Patient ID: {hit.get('patient_id')}")
            print(f"Context Text Snippet (First 200 chars):\n{hit.get('text', '')[:200]}...")

    except Exception as e:
        print(f"❌ Search Query Failed: {str(e)}")


if __name__ == "__main__":
    run_rag_validation()
