from abc import ABC, abstractmethod
import os
import tempfile
from groq import AsyncGroq
from app.config import settings
from app.utils.logging import logger

class STTProvider(ABC):
    """Abstract Base Class for Speech-To-Text providers."""

    @abstractmethod
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Transcribe raw audio bytes into text transcript."""
        pass


class WhisperSTT(STTProvider):
    """Whisper STT provider using Groq API (whisper-large-v3-turbo) with local Faster-Whisper fallback."""

    def __init__(self, model_name: str = "whisper-large-v3-turbo"):
        self.model_name = model_name
        self.api_key = settings.GROQ_API_KEY
        self.groq_client = AsyncGroq(api_key=self.api_key) if self.api_key else None
        self._local_model = None

    def _get_local_model(self):
        if self._local_model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info("Loading local Faster-Whisper model (tiny)...")
                self._local_model = WhisperModel("tiny", device="cpu", compute_type="int8")
                logger.info("Local Faster-Whisper model loaded.")
            except Exception as e:
                logger.error(f"Failed to load local Faster-Whisper model: {e}")
                self._local_model = False
        return self._local_model

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        if not audio_bytes or len(audio_bytes) < 100:
            logger.warning("Received empty or too small audio buffer for transcription.")
            return ""

        # Determine file extension prefix
        suffix = ".webm"
        if audio_bytes.startswith(b"RIFF"):
            suffix = ".wav"
        elif audio_bytes.startswith(b"OggS"):
            suffix = ".ogg"
        elif audio_bytes.startswith(b"ID3") or audio_bytes.startswith(b"\xff\xfb"):
            suffix = ".mp3"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        try:
            # 1. Try Groq Whisper API (Fastest & Most Accurate)
            if self.groq_client:
                logger.info(f"Transcribing audio buffer with Groq Whisper ({self.model_name})...")
                with open(tmp_path, "rb") as audio_file:
                    transcription = await self.groq_client.audio.transcriptions.create(
                        file=(f"speech{suffix}", audio_file, f"audio/{suffix.lstrip('.')}"),
                        model=self.model_name,
                        language="en"
                    )
                transcript = (transcription.text or "").strip()
                logger.info(f"STT Transcript (Groq): '{transcript}'")
                if transcript:
                    return transcript

            # 2. Local Faster-Whisper Fallback
            local_model = self._get_local_model()
            if local_model:
                logger.info("Transcribing audio buffer with local Faster-Whisper...")
                segments, info = local_model.transcribe(tmp_path, beam_size=1)
                transcript = " ".join([segment.text for segment in segments]).strip()
                logger.info(f"STT Transcript (Local): '{transcript}'")
                return transcript

            return ""
        except Exception as e:
            logger.error(f"Error during audio transcription: {e}")
            return ""
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
