from typing import List, Dict, Any
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import ChromaVectorStore
from app.config import settings
from app.utils.logging import logger

class Retriever:
    """Retriever for performing semantic search over embedded document chunks."""

    def __init__(self, embedding_service: EmbeddingService = None, vector_store: ChromaVectorStore = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or ChromaVectorStore()

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        k = top_k or settings.RAG_TOP_K
        if not query or not query.strip():
            return []

        logger.info(f"Retrieving top {k} context chunks for query: '{query[:60]}...'")
        query_vec = self.embedding_service.embed_query(query)
        chunks = self.vector_store.query(query_vec, top_k=k)
        return chunks

    def format_sources(self, retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        seen = set()

        for chunk in retrieved_chunks:
            meta = chunk.get("metadata", {})
            source_file = meta.get("source", "unknown")
            page = meta.get("page", 1)
            chunk_id = meta.get("chunk_id", "")

            key = (source_file, page)
            if key not in seen:
                seen.add(key)
                sources.append({
                    "source": source_file,
                    "page": page,
                    "chunk_id": chunk_id
                })

        return sources
