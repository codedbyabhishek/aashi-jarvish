from ashi_os.memory.memory_service import MemoryService


class ResearchAgent:
    def __init__(self, memory: MemoryService, top_k: int = 5) -> None:
        self.memory = memory
        self.top_k = top_k

    def run(self, session_id: str, objective: str) -> dict:
        hits = self.memory.search(session_id=session_id, query=objective, top_k=self.top_k)
        facts = [item.get("text", "") for item in hits if item.get("text")]
        return {
            "objective": objective,
            "memory_hits": len(hits),
            "facts": facts,
        }
