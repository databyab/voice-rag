from typing import List, Dict, Any, Optional
import threading

class SessionMemory:
    """In-memory thread-safe conversation history storage."""

    def __init__(self, max_history_turns: int = 4):
        self.max_history_turns = max_history_turns
        self._sessions: Dict[str, List[Dict[str, str]]] = {}
        self._lock = threading.Lock()

    def add_message(self, session_id: str, role: str, content: str):
        if not session_id:
            return

        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []
            
            self._sessions[session_id].append({
                "role": role,
                "content": content
            })

            # Keep only latest max_history_turns * 2 messages (user + assistant pairs)
            max_msgs = self.max_history_turns * 2
            if len(self._sessions[session_id]) > max_msgs:
                self._sessions[session_id] = self._sessions[session_id][-max_msgs:]

    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def get_formatted_history(self, session_id: str) -> str:
        messages = self.get_messages(session_id)
        if not messages:
            return "None"

        formatted = []
        for msg in messages:
            role_name = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role_name}: {msg['content']}")
        return "\n".join(formatted)

    def clear_session(self, session_id: str):
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

session_memory = SessionMemory()
