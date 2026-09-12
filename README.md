# Pipecat + RAG Conversational AI Assistant

A production-structured, locally runnable Conversational AI application built with **Pipecat** as the real-time voice pipeline framework, **Groq** for high-speed LLM generation, **ChromaDB** for local vector storage, **Sentence-Transformers** for local embedding generation, **FastAPI** backend, and a modern **React + Vite** frontend.

---

## 🌟 Architecture Overview

```text
                 ┌───────────────┐
                 │   Frontend    │
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              │                     │
            Chat                  Voice
              │                     │
              │                  Pipecat
              │                     │
              └──────────┬──────────┘
                         ↓
                   Conversation
                         ↓
                    RAG Service
                         ↓
                    Retriever
                         ↓
                    ChromaDB
                         ↓
                  Context Builder
                         ↓
                    Groq LLM
                         ↓
                  Response Stream
```

### Component Breakdown
- **Embedding Model**: Local `sentence-transformers/all-MiniLM-L6-v2` running on CPU/GPU without paid APIs.
- **Vector Database**: Local persistent **ChromaDB** at `./data/chroma/`.
- **Document Processing**: PDF (`pypdf`), Word (`python-docx`), Markdown (`.md`), Text (`.txt`).
- **LLM Provider**: **Groq** (`groq.AsyncGroq`) configured via `.env` (`GROQ_API_KEY`, `GROQ_MODEL`).
- **Voice Stack**:
  - `STTProvider` interface -> `WhisperSTT` (local Whisper model)
  - `TTSProvider` interface -> `LocalTTS` (Edge-TTS high quality neural voice)
  - `Pipecat` real-time WebSocket audio transport pipeline.
- **Frontend**: Glassmorphism UI built with React, Vite, Lucide icons, document upload, source citation badges, and real-time voice interaction.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 2. Backend Setup

Create virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` and set your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Frontend Setup

In a separate terminal window:
```bash
cd frontend
npm install
npm run dev
```

### 4. Running the Backend

```bash
python run.py
```

Open your browser at `http://localhost:3000` (or `http://localhost:8000`).

---

## 📚 Document Ingestion & RAG Flow

### CLI Document Ingestion
You can ingest documents via the frontend UI sidebar or CLI:
```bash
python scripts/ingest.py data/documents/sample_rag_guide.txt
```

### CLI RAG Test Query
```bash
python scripts/test_rag.py "What is Retrieval-Augmented Generation?"
```

---

## 🔁 Request Execution Flows

### Chat Request Flow
```text
User Message -> POST /api/chat -> RAG Service -> Query Embedding -> ChromaDB Search
   -> Top-K Chunks -> Prompt Builder + History -> Groq API -> Streaming Answer & Citations
```

### Voice Request Flow
```text
Browser Mic -> Audio Stream -> WebSocket /api/voice/ws -> Pipecat Pipeline
   -> Whisper STT -> Transcribed Text -> RAG Service -> Groq LLM
   -> Answer Text -> Edge-TTS Audio Synthesis -> WebSocket -> Browser Speaker
```

---

## 🧪 Running Unit & Integration Tests

```bash
pytest tests/ -v
```

Tests verify:
- Configurable text chunking and overlap logic
- Local Sentence-Transformer vector embedding dimensions (384-d)
- ChromaDB vector store insertion & top-K similarity search
- RAG service context formatting and source citations
- FastAPI `/api/health`, `/api/documents`, and `/api/chat` endpoints

---

## 🔧 Extensibility & Future Work

The system uses abstract provider patterns:
- **STT**: Swap `WhisperSTT` with Deepgram, AssemblyAI, or Vosk by implementing `STTProvider`.
- **TTS**: Swap `LocalTTS` with ElevenLabs, Coqui, or Piper by implementing `TTSProvider`.
- **Vector DB**: Replace `ChromaVectorStore` with Qdrant, Milvus, or PGVector.
- **LLM**: Add alternative adapters in `app/llm/` for Ollama, Anthropic, or OpenAI.
