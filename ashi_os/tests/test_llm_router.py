from pathlib import Path

from ashi_os.brain.llm_router import LLMRouter
from ashi_os.core.config import Settings


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
        wake_phrase="hey aashi",
        default_tts_voice="Samantha",
        voice_inbox_dir=Path("./data/voice/inbox"),
        voice_processed_dir=Path("./data/voice/processed"),
        voice_poll_interval_sec=1.0,
        mic_sample_rate=16000,
        mic_chunk_seconds=2.0,
        mic_channels=1,
        mic_device_index=None,
    )
    router = LLMRouter(settings)
    reply, provider, model = router.generate("hello")
    assert provider in {"none", "fallback", "ollama", "openai"}
    assert isinstance(reply, str)
    assert isinstance(model, str)
