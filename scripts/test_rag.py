import sys
import asyncio
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.rag.pipeline import rag_service
from app.utils.logging import logger

async def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "What is RAG and how does it work?"
    print(f"\nRunning test RAG query: '{query}'\n")

    try:
        res = await rag_service.answer_question(query)
        print("--- Answer ---")
        print(res.get("answer"))
        print("\n--- Source Citations ---")
        for src in res.get("sources", []):
            print(f"- {src['source']} (Page {src['page']}) [Chunk: {src.get('chunk_id')}]")
        print("---------------\n")
    except Exception as e:
        logger.error(f"Test RAG query failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
