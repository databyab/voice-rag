from typing import AsyncGenerator
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection
from pipecat.frames.frames import Frame, TextFrame, TranscriptionFrame, ErrorFrame
from app.rag.pipeline import RAGService, rag_service
from app.utils.logging import logger

class RAGProcessor(FrameProcessor):
    """Pipecat Processor that intercepts user text frames, executes RAG retrieval + Groq LLM, and emits answer frames."""

    def __init__(self, rag: RAGService = None, session_id: str = "voice_session"):
        super().__init__()
        self.rag = rag or rag_service
        self.session_id = session_id

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        user_text = None
        if isinstance(frame, TranscriptionFrame):
            user_text = frame.text
        elif isinstance(frame, TextFrame):
            user_text = frame.text

        if user_text and user_text.strip():
            logger.info(f"[Pipecat RAGProcessor] Processing user input frame: '{user_text}'")
            try:
                result = await self.rag.answer_question(user_text, session_id=self.session_id)
                answer_text = result.get("answer", "")
                
                logger.info(f"[Pipecat RAGProcessor] Pushing LLM output frame: '{answer_text[:60]}...'")
                out_frame = TextFrame(text=answer_text)
                await self.push_frame(out_frame, direction)
            except Exception as e:
                logger.error(f"[Pipecat RAGProcessor] Error during frame processing: {e}")
                err_frame = ErrorFrame(error=str(e))
                await self.push_frame(err_frame, direction)
        else:
            # Pass non-text frames downstream
            await self.push_frame(frame, direction)
