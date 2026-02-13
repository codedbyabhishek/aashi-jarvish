from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class AppConfig:
    memory_file: Path
    voice_files_dir: Path
    openai_model: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            memory_file=Path("aashi_memory.json"),
            voice_files_dir=Path("save"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )
