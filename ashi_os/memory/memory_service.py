import time
import uuid
from typing import Any

from ashi_os.core.config import Settings
from ashi_os.memory.vector_store import VectorStore


class MemoryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = VectorStore(settings)

    def add_memory(self, session_id: str, text: str, metadata: dict[str, Any] | None = None) -> str:
        memory_id = str(uuid.uuid4())
        payload = {
            "session_id": session_id,
            "created_at": int(time.time()),
        }
        if metadata:
            payload.update(metadata)
        self.store.add(memory_id, text, payload)
        return memory_id

    def search(self, session_id: str, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        limit = top_k if top_k is not None else self.settings.memory_top_k
        hits = self.store.query(query, limit)
        filtered = []
        for hit in hits:
            if hit.get("metadata", {}).get("session_id") == session_id:
                filtered.append(hit)
        return filtered
