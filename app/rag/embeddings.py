from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.utils.logging import logger

class EmbeddingService:
    """Local embedding service using HuggingFace Sentence Transformers."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        logger.info(f"Loading local embedding model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        logger.info("Local embedding model loaded successfully.")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        logger.info(f"Generating embeddings for {len(texts)} text segments...")
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            return []
        embedding = self.model.encode(query, show_progress_bar=False, convert_to_numpy=True)
        return embedding.tolist()
