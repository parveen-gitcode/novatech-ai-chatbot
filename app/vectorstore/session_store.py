from app.utils.helpers import logger

class SessionStore:
    """
    In-memory session store.
    Maintains conversation history per sessionId.
    Keeps only last 5 message pairs (10 messages total).
    """

    def __init__(self):
        self._sessions: dict[str, list[dict]] = {}
        self.MAX_HISTORY = 5  # Keep last 5 pairs

    def get_history(self, session_id: str) -> list[dict]:
        """Return conversation history for a given session."""
        return self._sessions.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to the session history.
        role: "user" or "assistant"
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = []
            logger.info(f"New session created: {session_id}")

        self._sessions[session_id].append({
            "role": role,
            "content": content
        })

        # ── Trim to last MAX_HISTORY pairs ────────────────────
        # Each pair = 1 user + 1 assistant message = 2 entries
        max_messages = self.MAX_HISTORY * 2
        if len(self._sessions[session_id]) > max_messages:
            self._sessions[session_id] = self._sessions[session_id][-max_messages:]
            logger.info(f"Session {session_id} trimmed to last {self.MAX_HISTORY} pairs.")

    def clear_session(self, session_id: str) -> None:
        """Clear history for a specific session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Session cleared: {session_id}")

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def get_all_sessions(self) -> list[str]:
        return list(self._sessions.keys())


# ── Single global instance used across the app ───────────────
session_store = SessionStore()