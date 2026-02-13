from typing import Any

from ashi_os.brain.context_manager import ContextManager
from ashi_os.brain.llm_router import LLMRouter
from ashi_os.core.security import is_destructive_command
from ashi_os.logging.audit_log import AuditLogger
from ashi_os.memory.memory_service import MemoryService


class Orchestrator:
    def __init__(
        self,
        router: LLMRouter,
        context_manager: ContextManager,
        memory: MemoryService,
        audit: AuditLogger,
        memory_on_chat: bool,
    ) -> None:
        self.router = router
        self.context_manager = context_manager
        self.memory = memory
        self.audit = audit
        self.memory_on_chat = memory_on_chat
        self._sessions: dict[str, list[dict[str, str]]] = {}

    def chat(self, session_id: str, user_message: str) -> tuple[str, str, str]:
        if is_destructive_command(user_message):
            confirmation = "Risk level elevated. Confirmation required before destructive operations."
            self.audit.write("blocked.destructive", {"session_id": session_id, "message": user_message})
            return confirmation, "policy", "confirm_gate"

        history = self._sessions.setdefault(session_id, [])
        prompt = self.context_manager.build(session_id, user_message, history)
        reply, provider, model = self.router.generate(prompt)

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})

        if self.memory_on_chat and len(user_message.strip()) > 8:
            self.memory.add_memory(session_id, user_message, {"kind": "user_fact"})

        self.audit.write(
            "chat.completed",
            {
                "session_id": session_id,
                "provider": provider,
                "model": model,
                "user_message": user_message,
                "reply": reply,
            },
        )
        return reply, provider, model

    def session_history(self, session_id: str) -> list[dict[str, str]]:
        return list(self._sessions.get(session_id, []))
