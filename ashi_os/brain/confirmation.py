from dataclasses import dataclass
from datetime import datetime, timezone
import secrets


@dataclass
class PendingConfirmation:
    token: str
    original_message: str
    created_at_iso: str


class ConfirmationManager:
    def __init__(self) -> None:
        self._pending: dict[str, PendingConfirmation] = {}

    def create(self, session_id: str, original_message: str) -> str:
        token = secrets.token_hex(4)
        self._pending[session_id] = PendingConfirmation(
            token=token,
            original_message=original_message,
            created_at_iso=datetime.now(timezone.utc).isoformat(),
        )
        return token

    def consume_if_valid(self, session_id: str, user_message: str) -> tuple[bool, str]:
        pending = self._pending.get(session_id)
        if pending is None:
            return False, ""

        normalized = user_message.strip().lower()
        expected = f"confirm {pending.token}"
        if normalized == expected:
            del self._pending[session_id]
            return True, pending.original_message

        if normalized.startswith("confirm "):
            return True, ""

        return False, ""

    def has_pending(self, session_id: str) -> bool:
        return session_id in self._pending

    def pending_token(self, session_id: str) -> str | None:
        pending = self._pending.get(session_id)
        return pending.token if pending else None

    def consume_token(self, session_id: str, token: str) -> tuple[bool, str]:
        pending = self._pending.get(session_id)
        if pending is None:
            return False, ""
        if token.strip() == pending.token:
            del self._pending[session_id]
            return True, pending.original_message
        return False, ""
