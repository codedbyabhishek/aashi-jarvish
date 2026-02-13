import json
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, memory_file: str = "aashi_memory.json") -> None:
        self.path = Path(memory_file)
        self.data: dict[str, Any] = {
            "notes": [],
            "voice": {
                "enabled": False,
                "name": "Samantha",
                "mode": "system",
                "file": "",
            },
        }
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return

        try:
            with self.path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                self.data = loaded
                self.data.setdefault("notes", [])
                self.data.setdefault("voice", {})
                self.data["voice"].setdefault("enabled", False)
                self.data["voice"].setdefault("name", "Samantha")
                self.data["voice"].setdefault("mode", "system")
                self.data["voice"].setdefault("file", "")
        except (OSError, json.JSONDecodeError):
            self.data = {
                "notes": [],
                "voice": {
                    "enabled": False,
                    "name": "Samantha",
                    "mode": "system",
                    "file": "",
                },
            }

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def add_note(self, text: str) -> None:
        self.data.setdefault("notes", []).append(text)
        self.save()

    def notes(self) -> list[str]:
        return list(self.data.get("notes", []))

    def voice_enabled(self) -> bool:
        voice = self.data.get("voice", {})
        return bool(voice.get("enabled", False))

    def voice_name(self) -> str:
        voice = self.data.get("voice", {})
        return str(voice.get("name", "Samantha"))

    def set_voice_enabled(self, enabled: bool) -> None:
        self.data.setdefault("voice", {})
        self.data["voice"]["enabled"] = enabled
        self.save()

    def set_voice_name(self, name: str) -> None:
        self.data.setdefault("voice", {})
        self.data["voice"]["name"] = name
        self.save()

    def voice_mode(self) -> str:
        voice = self.data.get("voice", {})
        mode = str(voice.get("mode", "system"))
        if mode not in {"system", "file"}:
            return "system"
        return mode

    def set_voice_mode(self, mode: str) -> None:
        self.data.setdefault("voice", {})
        self.data["voice"]["mode"] = mode
        self.save()

    def voice_file(self) -> str:
        voice = self.data.get("voice", {})
        return str(voice.get("file", ""))

    def set_voice_file(self, filename: str) -> None:
        self.data.setdefault("voice", {})
        self.data["voice"]["file"] = filename
        self.save()
