import pytest
from app.rag.chunking import TextChunker

def test_chunk_size_and_overlap():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    sample_text = "Word " * 50  # 250 chars
    
    docs = [{
        "content": sample_text,
        "metadata": {"source": "test.txt", "page": 1}
    }]
    
    chunks = chunker.split_documents(docs)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c["content"]) <= 100
        assert "chunk_id" in c["metadata"]
        assert c["metadata"]["source"] == "test.txt"

def test_empty_document():
    chunker = TextChunker()
    docs = [{"content": "", "metadata": {"source": "empty.txt", "page": 1}}]
    chunks = chunker.split_documents(docs)
    assert len(chunks) == 0
