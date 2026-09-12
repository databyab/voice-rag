from typing import Dict, Any, List, AsyncGenerator, Tuple
from app.rag.ingestion import DocumentLoader
from app.rag.chunking import TextChunker
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import ChromaVectorStore
from app.rag.retriever import Retriever
from app.llm.groq_client import GroqClient
from app.conversation.memory import session_memory
from app.utils.logging import logger

class RAGService:
    """Core RAG Service coordinating ingestion, retrieval, prompt assembly, and LLM responses."""

    def __init__(self,
                 embedding_service: EmbeddingService = None,
                 vector_store: ChromaVectorStore = None,
                 retriever: Retriever = None,
                 groq_client: GroqClient = None):

        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or ChromaVectorStore()
        self.retriever = retriever or Retriever(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store
        )
        self.groq_client = groq_client or GroqClient()
        self.chunker = TextChunker()

    def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """Loads, parses, chunks, embeds, and stores a document in vector store."""
        pages = DocumentLoader.load_document(file_path)
        if not pages:
            return {"filename": file_path, "chunks_created": 0, "status": "empty"}

        chunks = self.chunker.split_documents(pages)
        if not chunks:
            return {"filename": file_path, "chunks_created": 0, "status": "empty"}

        texts = [c["content"] for c in chunks]
        embeddings = self.embedding_service.embed_texts(texts)

        inserted_count = self.vector_store.add_chunks(chunks, embeddings)
        filename = chunks[0]["metadata"].get("source", file_path)

        return {
            "filename": filename,
            "chunks_created": inserted_count,
            "status": "success"
        }

    async def answer_question(self, question: str, session_id: str = "default") -> Dict[str, Any]:
        """Generates answer to question using RAG and returns answer with source citations."""
        logger.info(f"Processing chat query (session_id={session_id}): '{question[:60]}...'")

        # Fast path check for hardcoded greetings & farewells
        clean_q = question.strip().lower().strip(".!?,")
        greetings = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings", "hi there", "hello there"}
        farewells = {"bye", "goodbye", "see you", "see ya", "talk to you later", "have a nice day", "farewell", "cya"}

        if clean_q in greetings:
            answer = "Hello! I am your AI assistant. How can I help you with your documents today?"
            session_memory.add_message(session_id, "user", question)
            session_memory.add_message(session_id, "assistant", answer)
            return {"answer": answer, "sources": []}

        if clean_q in farewells:
            answer = "Goodbye! Feel free to reach out anytime if you have more questions."
            session_memory.add_message(session_id, "user", question)
            session_memory.add_message(session_id, "assistant", answer)
            return {"answer": answer, "sources": []}

        # 1. Retrieve relevant chunks
        chunks = self.retriever.retrieve(question)
        sources = self.retriever.format_sources(chunks)

        # 2. Build context string
        context_parts = []
        for i, chunk in enumerate(chunks, start=1):
            src_name = chunk.get("metadata", {}).get("source", "doc")
            page_num = chunk.get("metadata", {}).get("page", 1)
            context_parts.append(f"--- Context Segment {i} [Source: {src_name}, Page: {page_num}] ---\n{chunk['content']}")

        context_str = "\n\n".join(context_parts)

        # 3. Retrieve conversation history
        history_str = session_memory.get_formatted_history(session_id)

        # 4. Generate answer from Groq
        answer = await self.groq_client.generate_response(
            question=question,
            context=context_str,
            history=history_str
        )

        # 5. Save turn into memory
        session_memory.add_message(session_id, "user", question)
        session_memory.add_message(session_id, "assistant", answer)

        return {
            "answer": answer,
            "sources": sources
        }

    async def answer_question_stream(self, question: str, session_id: str = "default") -> Tuple[AsyncGenerator[str, None], List[Dict[str, Any]]]:
        """Generates a streaming answer to question using RAG."""
        logger.info(f"Processing streaming chat query (session_id={session_id}): '{question[:60]}...'")

        chunks = self.retriever.retrieve(question)
        sources = self.retriever.format_sources(chunks)

        context_parts = []
        for i, chunk in enumerate(chunks, start=1):
            src_name = chunk.get("metadata", {}).get("source", "doc")
            page_num = chunk.get("metadata", {}).get("page", 1)
            context_parts.append(f"--- Context Segment {i} [Source: {src_name}, Page: {page_num}] ---\n{chunk['content']}")

        context_str = "\n\n".join(context_parts)
        history_str = session_memory.get_formatted_history(session_id)

        # We record the question now
        session_memory.add_message(session_id, "user", question)

        stream = self.groq_client.generate_stream(
            question=question,
            context=context_str,
            history=history_str
        )

        return stream, sources

    def list_indexed_documents(self) -> List[Dict[str, Any]]:
        return self.vector_store.list_documents()

rag_service = RAGService()
