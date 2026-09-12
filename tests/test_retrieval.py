import pytest
from app.rag.vector_store import ChromaVectorStore
from app.rag.retriever import Retriever

def test_vector_store_and_retriever(tmp_path):
    store = ChromaVectorStore(chroma_path=str(tmp_path / "test_chroma"))
    
    sample_chunks = [
        {
            "chunk_id": "c1",
            "content": "Pipecat is a framework for voice applications.",
            "metadata": {"source": "guide.txt", "page": 1, "chunk_id": "c1"}
        },
        {
            "chunk_id": "c2",
            "content": "Groq provides ultra-fast LLM inference API.",
            "metadata": {"source": "guide.txt", "page": 2, "chunk_id": "c2"}
        }
    ]
    
    retriever = Retriever(vector_store=store)
    embeddings = retriever.embedding_service.embed_texts([c["content"] for c in sample_chunks])
    
    store.add_chunks(sample_chunks, embeddings)
    
    results = retriever.retrieve("Tell me about voice framework", top_k=1)
    assert len(results) == 1
    assert "Pipecat" in results[0]["content"]
    
    sources = retriever.format_sources(results)
    assert len(sources) == 1
    assert sources[0]["source"] == "guide.txt"
    assert sources[0]["page"] == 1
