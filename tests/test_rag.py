import pytest
from unittest.mock import AsyncMock, MagicMock
from app.rag.pipeline import RAGService
from app.conversation.memory import SessionMemory

@pytest.mark.asyncio
async def test_rag_pipeline_answer():
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [
        {
            "content": "RAG enhances LLM with external search.",
            "metadata": {"source": "rag_intro.pdf", "page": 3, "chunk_id": "chunk_01"}
        }
    ]
    mock_retriever.format_sources.return_value = [
        {"source": "rag_intro.pdf", "page": 3, "chunk_id": "chunk_01"}
    ]

    mock_groq = MagicMock()
    mock_groq.generate_response = AsyncMock(return_value="RAG stands for Retrieval-Augmented Generation.")

    rag = RAGService(retriever=mock_retriever, groq_client=mock_groq)

    res = await rag.answer_question("What is RAG?", session_id="test_session")

    assert res["answer"] == "RAG stands for Retrieval-Augmented Generation."
    assert len(res["sources"]) == 1
    assert res["sources"][0]["source"] == "rag_intro.pdf"
    assert res["sources"][0]["page"] == 3
