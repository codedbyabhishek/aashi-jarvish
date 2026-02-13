from pathlib import Path
from typing import Optional


class VoiceInputEngine:
    def __init__(self, voice_files_dir: Path, api_key: Optional[str]) -> None:
        self.voice_files_dir = voice_files_dir
        self.api_key = api_key or ""
        self._client = None

        if not self.api_key:
            return

        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        except Exception:
            self._client = None

    def transcribe_file(self, filename: str) -> tuple[bool, str]:
        file_path = self.voice_files_dir / filename
        if not file_path.exists() or not file_path.is_file():
            return False, "Audio file not found in ./save."

        if not self._client:
            return False, "Set OPENAI_API_KEY and install openai to use voice input."

        try:
            with file_path.open("rb") as audio_file:
                result = self._client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=audio_file,
                )
            text = str(getattr(result, "text", "")).strip()
            if not text:
                return False, "Could not transcribe that audio."
            return True, text
        except Exception:
            return False, "Voice transcription failed."

    def has_api_key(self) -> bool:
        return bool(self.api_key.strip())
