import os
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.config import settings
from app.api import chat_router, documents_router
from app.pipecat import WebSocketVoiceTransport
from app.utils.logging import logger

app = FastAPI(
    title="Pipecat + RAG Conversational AI API",
    description="Production-structured RAG Conversational AI Assistant using Groq, ChromaDB, Sentence-Transformers, and Pipecat",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat_router)
app.include_router(documents_router)

# WebSocket Endpoint for Pipecat Voice Pipeline
@app.websocket("/api/voice/ws")
async def voice_websocket_endpoint(websocket: WebSocket, session_id: str = "voice_session"):
    await WebSocketVoiceTransport.handle_websocket(websocket, session_id=session_id)

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "groq_model": settings.GROQ_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "chroma_path": settings.CHROMA_PATH
    }

# Mount static frontend if dist folder exists
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/static", StaticFiles(directory=frontend_dist), name="static")

    @app.get("/")
    async def serve_frontend():
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"message": "Pipecat RAG API Server Running."})

logger.info("FastAPI application initialized successfully.")
