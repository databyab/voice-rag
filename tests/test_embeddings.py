import pytest
from app.rag.embeddings import EmbeddingService

def test_embed_texts():
    service = EmbeddingService()
    texts = ["Retrieval-Augmented Generation", "Pipecat voice assistant"]
    embeddings = service.embed_texts(texts)
    
    assert len(embeddings) == 2
    # sentence-transformers/all-MiniLM-L6-v2 dimension is 384
    assert len(embeddings[0]) == 384

def test_embed_query():
    service = EmbeddingService()
    vec = service.embed_query("What is ChromaDB?")
    assert isinstance(vec, list)
    assert len(vec) == 384
