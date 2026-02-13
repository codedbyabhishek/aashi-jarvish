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


def get_settings() -> Settings:
    chroma_dir = Path(os.getenv("CHROMA_DIR", "./data/chroma"))
    sqlite_path = Path(os.getenv("SQLITE_PATH", "./data/state.db"))
    log_dir = Path(os.getenv("LOG_DIR", "./data/logs"))

    chroma_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

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
    )
