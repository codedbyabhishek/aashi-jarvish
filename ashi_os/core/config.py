from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    env: str
    default_llm: str
    fallback_llm: str
    ollama_model: str
    openai_model: str
    openai_api_key: str
    chroma_dir: Path
    sqlite_path: Path
    log_dir: Path
    max_context_tokens: int
    memory_top_k: int
    memory_on_chat: bool
    wake_phrase: str
    default_tts_voice: str
    voice_inbox_dir: Path
    voice_processed_dir: Path
    voice_poll_interval_sec: float
    mic_sample_rate: int
    mic_chunk_seconds: float
    mic_channels: int
    mic_device_index: int | None


def get_settings() -> Settings:
    chroma_dir = Path(os.getenv("CHROMA_DIR", "./data/chroma"))
    sqlite_path = Path(os.getenv("SQLITE_PATH", "./data/state.db"))
    log_dir = Path(os.getenv("LOG_DIR", "./data/logs"))

    chroma_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    voice_inbox_dir = Path(os.getenv("VOICE_INBOX_DIR", "./data/voice/inbox"))
    voice_processed_dir = Path(os.getenv("VOICE_PROCESSED_DIR", "./data/voice/processed"))
    voice_inbox_dir.mkdir(parents=True, exist_ok=True)
    voice_processed_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        env=os.getenv("ASHI_ENV", "local"),
        default_llm=os.getenv("ASHI_DEFAULT_LLM", "ollama"),
        fallback_llm=os.getenv("ASHI_FALLBACK_LLM", "openai"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        chroma_dir=chroma_dir,
        sqlite_path=sqlite_path,
        log_dir=log_dir,
        max_context_tokens=int(os.getenv("MAX_CONTEXT_TOKENS", "8000")),
        memory_top_k=int(os.getenv("MEMORY_TOP_K", "8")),
        memory_on_chat=os.getenv("MEMORY_ON_CHAT", "false").strip().lower() == "true",
        wake_phrase=os.getenv("WAKE_PHRASE", "hey aashi").strip() or "hey aashi",
        default_tts_voice=os.getenv("DEFAULT_TTS_VOICE", "Samantha").strip() or "Samantha",
        voice_inbox_dir=voice_inbox_dir,
        voice_processed_dir=voice_processed_dir,
        voice_poll_interval_sec=float(os.getenv("VOICE_POLL_INTERVAL_SEC", "1.0")),
        mic_sample_rate=int(os.getenv("MIC_SAMPLE_RATE", "16000")),
        mic_chunk_seconds=float(os.getenv("MIC_CHUNK_SECONDS", "2.0")),
        mic_channels=int(os.getenv("MIC_CHANNELS", "1")),
        mic_device_index=int(os.getenv("MIC_DEVICE_INDEX")) if os.getenv("MIC_DEVICE_INDEX") else None,
    )
