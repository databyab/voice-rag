import json
import base64
from fastapi import WebSocket, WebSocketDisconnect
from app.pipecat.pipeline import voice_pipeline_manager
from app.utils.logging import logger

class WebSocketVoiceTransport:
    """WebSocket Transport for real-time voice pipeline connection."""

    @staticmethod
    async def handle_websocket(websocket: WebSocket, session_id: str = "voice_session"):
        await websocket.accept()
        logger.info(f"Pipecat WebSocket audio session started (session_id={session_id}).")

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                msg_type = message.get("type")
                if msg_type == "audio_input":
                    audio_b64 = message.get("audio", "")
                    audio_bytes = base64.b64decode(audio_b64) if audio_b64 else b""
                    
                    async for event in voice_pipeline_manager.process_audio_interaction(audio_bytes, session_id=session_id):
                        await websocket.send_json(event)
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
        except WebSocketDisconnect:
            logger.info(f"Pipecat WebSocket audio session ended (session_id={session_id}).")
        except Exception as e:
            logger.error(f"WebSocket transport error: {e}")
            try:
                await websocket.send_json({"state": "error", "message": str(e)})
            except Exception:
                pass
