from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.rag.pipeline import rag_service
from app.utils.logging import logger
import json

router = APIRouter(prefix="/api", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str = Field(..., description="The query string from the user")
    session_id: Optional[str] = Field(default="default", description="Session identifier for memory tracking")
    stream: Optional[bool] = Field(default=False, description="Whether to stream response tokens")

class SourceCitation(BaseModel):
    source: str
    page: int
    chunk_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        if request.stream:
            # Handle streaming in chat endpoint
            stream, sources = await rag_service.answer_question_stream(request.message, session_id=request.session_id)
            
            async def event_generator():
                # Send sources first
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
                async for chunk in stream:
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")
        else:
            result = await rag_service.answer_question(request.message, session_id=request.session_id)
            return ChatResponse(
                answer=result["answer"],
                sources=result["sources"]
            )
    except ValueError as e:
        logger.error(f"Chat request validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat endpoint failure: {e}")
        raise HTTPException(status_code=500, detail=f"Internal RAG processing error: {str(e)}")
