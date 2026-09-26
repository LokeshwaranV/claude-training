"""Session management for chat conversations."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from models.schemas import ChatMessage, MessageRole, Session, SpecialtyEnum


class SessionManager:
    """Manage chat sessions and conversation history."""

    def __init__(self, storage_path: str = "./data/sessions"):
        """Initialize session manager."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def create_session(
        self,
        user_id: str,
        patient_id: str,
        specialty: SpecialtyEnum = SpecialtyEnum.GENERAL_PRACTICE
    ) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            user_id=user_id,
            patient_id=patient_id,
            specialty=specialty
        )
        self._save_session(session)
        return session_id

    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str
    ) -> None:
        """Add message to session."""
        session = self._load_session(session_id)
        if session:
            message = ChatMessage(role=role, content=content)
            session.messages.append(message)
            session.updated_at = datetime.utcnow()
            self._save_session(session)

    def get_conversation_history(self, session_id: str) -> List[ChatMessage]:
        """Get conversation history for session."""
        session = self._load_session(session_id)
        return session.messages if session else []

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session details."""
        return self._load_session(session_id)

    def end_session(self, session_id: str) -> bool:
        """End a session."""
        session_file = self.storage_path / f"{session_id}.json"
        if session_file.exists():
            # Archive session
            archive_path = self.storage_path / "archive"
            archive_path.mkdir(exist_ok=True)
            session_file.rename(archive_path / f"{session_id}.json")
            return True
        return False

    def list_sessions(self, user_id: str) -> List[str]:
        """List sessions for a user."""
        sessions = []
        for session_file in self.storage_path.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    if data.get('user_id') == user_id:
                        sessions.append(data.get('session_id'))
            except Exception:
                continue
        return sessions

    def _save_session(self, session: Session) -> None:
        """Save session to disk."""
        session_file = self.storage_path / f"{session.session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session.model_dump(), f, default=str, indent=2)

    def _load_session(self, session_id: str) -> Optional[Session]:
        """Load session from disk."""
        session_file = self.storage_path / f"{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                data = json.load(f)
                # Convert message dicts to ChatMessage objects
                messages = [
                    ChatMessage(**msg) for msg in data.get('messages', [])
                ]
                data['messages'] = messages
                return Session(**data)
        return None

    def clear_old_sessions(self, days: int = 30) -> int:
        """Clean up sessions older than specified days."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = 0

        for session_file in self.storage_path.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    updated_at = datetime.fromisoformat(data.get('updated_at', ''))
                    if updated_at < cutoff_date:
                        session_file.unlink()
                        deleted += 1
            except Exception:
                continue

        return deleted
