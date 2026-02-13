from ashi_os.memory.memory_service import MemoryService


class MemoryAgent:
    def __init__(self, memory: MemoryService) -> None:
        self.memory = memory

    def store_reflection(self, session_id: str, objective: str, validation: dict) -> dict:
        text = (
            f"Objective: {objective} | "
            f"status: {'ok' if validation.get('ok') else 'needs_review'} | "
            f"summary: {validation.get('summary', '')}"
        )
        item_id = self.memory.add_memory(session_id=session_id, text=text, metadata={"kind": "agent_reflection"})
        return {"ok": True, "memory_id": item_id}
