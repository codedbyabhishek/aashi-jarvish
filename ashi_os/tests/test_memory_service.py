from pathlib import Path

from ashi_os.core.config import Settings
from ashi_os.memory.memory_service import MemoryService


def test_memory_add_and_search_non_crash() -> None:
    settings = Settings(
        env="test",
        default_llm="ollama",
        fallback_llm="openai",
        ollama_model="model",
        openai_model="model",
        openai_api_key="",
        chroma_dir=Path("./data/chroma"),
        sqlite_path=Path("./data/state.db"),
        log_dir=Path("./data/logs"),
        max_context_tokens=8000,
        memory_top_k=3,
        memory_on_chat=False,
    )
    memory = MemoryService(settings)
    memory.add_memory("s1", "remember this", {"tag": "x"})
    hits = memory.search("s1", "remember", 3)
    assert isinstance(hits, list)
