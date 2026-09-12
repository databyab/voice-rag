import os
import chromadb
from typing import List, Dict, Any
from app.config import settings
from app.utils.logging import logger

class ChromaVectorStore:
    """Persistent ChromaDB vector store adapter."""

    COLLECTION_NAME = "rag_documents"

    def __init__(self, chroma_path: str = None):
        self.chroma_path = chroma_path or settings.CHROMA_PATH
        os.makedirs(self.chroma_path, exist_ok=True)
        logger.info(f"Initializing persistent ChromaDB at {self.chroma_path}")
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
        if not chunks or not embeddings:
            return 0

        ids = [c["chunk_id"] for c in chunks]
        documents = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        logger.info(f"Storing {len(ids)} chunks in ChromaDB collection '{self.COLLECTION_NAME}'...")
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        return len(ids)

    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if not query_embedding:
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        matched_chunks = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, dists):
                matched_chunks.append({
                    "content": doc,
                    "metadata": meta,
                    "score": round(1.0 - float(dist), 4) if dist is not None else 1.0
                })

        logger.info(f"ChromaDB returned {len(matched_chunks)} chunks for query.")
        return matched_chunks

    def list_documents(self) -> List[Dict[str, Any]]:
        all_data = self.collection.get(include=["metadatas"])
        if not all_data or not all_data.get("metadatas"):
            return []

        doc_stats: Dict[str, Dict[str, Any]] = {}
        for meta in all_data["metadatas"]:
            source = meta.get("source", "unknown")
            page = meta.get("page", 1)
            file_type = meta.get("file_type", "")
            
            if source not in doc_stats:
                doc_stats[source] = {
                    "filename": source,
                    "file_type": file_type,
                    "chunks_count": 0,
                    "pages_count": set()
                }
            doc_stats[source]["chunks_count"] += 1
            doc_stats[source]["pages_count"].add(page)

        output = []
        for src, stat in doc_stats.items():
            output.append({
                "filename": stat["filename"],
                "file_type": stat["file_type"],
                "chunks_count": stat["chunks_count"],
                "total_pages": len(stat["pages_count"])
            })
        return output

    def reset_collection(self):
        logger.info(f"Resetting ChromaDB collection '{self.COLLECTION_NAME}'")
        self.client.delete_collection(self.COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
