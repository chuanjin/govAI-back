import uuid
from collections import defaultdict
from govai.config import settings


class SessionManager:
    """In-memory session manager that maintains conversation context."""

    def __init__(self):
        self._sessions: dict[str, list[dict]] = defaultdict(list)

    def get_or_create_session(self, session_id: str | None) -> str:
        if session_id and session_id in self._sessions:
            return session_id
        new_id = session_id or str(uuid.uuid4())
        self._sessions[new_id] = []
        return new_id

    def add_message(self, session_id: str, role: str, content: str):
        self._sessions[session_id].append({"role": role, "content": content})
        # Keep only the last N messages
        max_msgs = settings.max_context_messages
        if len(self._sessions[session_id]) > max_msgs:
            self._sessions[session_id] = self._sessions[session_id][-max_msgs:]

    def get_history(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])

    def clear_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]


session_manager = SessionManager()
