import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.pipeline import rag_service
from app.utils.logging import logger

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest.py <path_to_document>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    logger.info(f"Starting CLI ingestion for file: {file_path}")
    result = rag_service.ingest_file(file_path)
    print("\n--- Ingestion Result ---")
    print(f"Filename: {result.get('filename')}")
    print(f"Chunks Created: {result.get('chunks_created')}")
    print(f"Status: {result.get('status')}")
    print("------------------------\n")

if __name__ == "__main__":
    main()
