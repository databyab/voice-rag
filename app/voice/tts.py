from abc import ABC, abstractmethod
import edge_tts
from app.utils.logging import logger

class TTSProvider(ABC):
    """Abstract Base Class for Text-To-Speech providers."""

    @abstractmethod
    async def synthesize_speech(self, text: str) -> bytes:
        """Synthesize input text into audio bytes (e.g., MP3/WAV)."""
        pass


class LocalTTS(TTSProvider):
    """Free local high-quality neural TTS using Edge-TTS."""

    def __init__(self, voice: str = "en-US-AvaNeural"):
        self.voice = voice

    async def synthesize_speech(self, text: str) -> bytes:
        if not text or not text.strip():
            return b""

        logger.info(f"Synthesizing speech for text ({len(text)} chars) with voice '{self.voice}'...")
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            audio_bytes = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])

            logger.info(f"TTS synthesis completed ({len(audio_bytes)} audio bytes generated).")
            return bytes(audio_bytes)
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return b""
