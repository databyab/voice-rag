from typing import Dict, Any, AsyncGenerator
import base64
from app.voice.stt import STTProvider, WhisperSTT
from app.voice.tts import TTSProvider, LocalTTS
from app.rag.pipeline import RAGService, rag_service
from app.utils.logging import logger

class VoicePipelineManager:
    """Orchestrates real-time Voice Pipeline (STT -> RAG -> LLM -> TTS)."""

    def __init__(self,
                 stt_provider: STTProvider = None,
                 tts_provider: TTSProvider = None,
                 rag_service_inst: RAGService = None):

        self.stt = stt_provider or WhisperSTT()
        self.tts = tts_provider or LocalTTS()
        self.rag = rag_service_inst or rag_service

    async def process_audio_interaction(self, audio_bytes: bytes, session_id: str = "voice_session") -> AsyncGenerator[Dict[str, Any], None]:
        """Runs full voice pipeline step-by-step and streams status + audio results."""
        
        # Step 1: STT
        yield {"state": "listening", "message": "Transcribing audio..."}
        transcript = await self.stt.transcribe_audio(audio_bytes)
        
        if not transcript or not transcript.strip():
            yield {"state": "error", "message": "Could not recognize any speech in the audio."}
            return

        yield {"state": "thinking", "transcript": transcript, "message": "Retrieving context & generating answer..."}

        # Step 2: RAG + LLM
        try:
            rag_result = await self.rag.answer_question(transcript, session_id=session_id)
            answer_text = rag_result.get("answer", "")
            sources = rag_result.get("sources", [])
        except Exception as e:
            logger.error(f"RAG processing failed in voice pipeline: {e}")
            yield {"state": "error", "message": f"RAG error: {str(e)}"}
            return

        yield {"state": "speaking", "transcript": transcript, "answer": answer_text, "sources": sources, "message": "Synthesizing audio..."}

        # Step 3: TTS
        audio_out = await self.tts.synthesize_speech(answer_text)
        audio_b64 = base64.b64encode(audio_out).decode("utf-8") if audio_out else ""

        yield {
            "state": "completed",
            "transcript": transcript,
            "answer": answer_text,
            "sources": sources,
            "audio": audio_b64
        }

voice_pipeline_manager = VoicePipelineManager()
