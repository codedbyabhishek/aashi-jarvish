from pathlib import Path

from ashi_os.brain.context_manager import ContextManager
from ashi_os.core.config import Settings
from ashi_os.memory.memory_service import MemoryService


def test_context_manager_builds_prompt() -> None:
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
    context = ContextManager(settings, memory)
    out = context.build("s1", "plan next task", [{"role": "user", "content": "hello"}])
    assert "[USER_REQUEST]" in out
    assert "plan next task" in out
