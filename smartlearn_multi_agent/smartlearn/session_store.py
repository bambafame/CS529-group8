from __future__ import annotations

from typing import Dict

from .schemas import SessionRecord


class SessionStore:
    def __init__(self) -> None:
        self._store: Dict[str, SessionRecord] = {}

    def get_or_create(self, session_id: str) -> SessionRecord:
        if session_id not in self._store:
            self._store[session_id] = SessionRecord(session_id=session_id)
        return self._store[session_id]

    def get(self, session_id: str) -> SessionRecord | None:
        return self._store.get(session_id)
