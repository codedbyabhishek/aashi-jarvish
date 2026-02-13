import json
from pathlib import Path
from typing import Any


DEFAULT_STATE: dict[str, Any] = {
    "notes": [],
    "voice": {
        "enabled": False,
        "name": "Samantha",
        "mode": "system",
        "file": "",
    },
}


class MemoryStore:
    def __init__(self, memory_file: Path) -> None:
        self.path = memory_file
        self.data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.data = json.loads(json.dumps(DEFAULT_STATE))
            return

        try:
            with self.path.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (OSError, json.JSONDecodeError):
            self.data = json.loads(json.dumps(DEFAULT_STATE))
            return

        if not isinstance(loaded, dict):
            self.data = json.loads(json.dumps(DEFAULT_STATE))
            return

        self.data = loaded
        self._normalize()

    def _normalize(self) -> None:
        self.data.setdefault("notes", [])

        voice = self.data.setdefault("voice", {})
        if not isinstance(voice, dict):
            voice = {}
            self.data["voice"] = voice

        voice.setdefault("enabled", False)
        voice.setdefault("name", "Samantha")
        voice.setdefault("mode", "system")
        voice.setdefault("file", "")

        if voice["mode"] not in {"system", "file"}:
            voice["mode"] = "system"

    def save(self) -> None:
        self._normalize()
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2)

    def notes(self) -> list[str]:
        raw = self.data.get("notes", [])
        if not isinstance(raw, list):
            return []
        return [str(item) for item in raw]

    def add_note(self, text: str) -> None:
        notes = self.notes()
        notes.append(text)
        self.data["notes"] = notes
        self.save()

    def voice_enabled(self) -> bool:
        return bool(self.data.get("voice", {}).get("enabled", False))

    def set_voice_enabled(self, enabled: bool) -> None:
        self.data.setdefault("voice", {})["enabled"] = enabled
        self.save()

    def voice_name(self) -> str:
        return str(self.data.get("voice", {}).get("name", "Samantha"))

    def set_voice_name(self, name: str) -> None:
        self.data.setdefault("voice", {})["name"] = name
        self.save()

    def voice_mode(self) -> str:
        mode = str(self.data.get("voice", {}).get("mode", "system"))
        return mode if mode in {"system", "file"} else "system"

    def set_voice_mode(self, mode: str) -> None:
        self.data.setdefault("voice", {})["mode"] = mode
        self.save()

    def voice_file(self) -> str:
        return str(self.data.get("voice", {}).get("file", ""))

    def set_voice_file(self, filename: str) -> None:
        self.data.setdefault("voice", {})["file"] = filename
        self.save()
