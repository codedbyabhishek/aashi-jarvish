from ashi_os.brain.llm_router import LLMRouter
from ashi_os.core.config import Settings
from pathlib import Path


def test_router_returns_fallback_message_when_no_backends() -> None:
    settings = Settings(
        env="test",
        default_llm="openai",
        fallback_llm="ollama",
        ollama_model="none",
        openai_model="none",
        openai_api_key="",
        chroma_dir=Path("./data/chroma"),
        sqlite_path=Path("./data/state.db"),
        log_dir=Path("./data/logs"),
        max_context_tokens=8000,
        memory_top_k=8,
        memory_on_chat=False,
    )
    router = LLMRouter(settings)
    reply, provider, model = router.generate("hello")
    assert provider in {"none", "fallback", "ollama", "openai"}
    assert isinstance(reply, str)
    assert isinstance(model, str)
