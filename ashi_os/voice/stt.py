from pathlib import Path


class SpeechToTextService:
    def __init__(self, openai_api_key: str) -> None:
        self.openai_api_key = openai_api_key

    def transcribe_file(self, file_path: Path) -> tuple[bool, str]:
        if not file_path.exists() or not file_path.is_file():
            return False, "Audio file not found."
        if not self.openai_api_key:
            return False, "OPENAI_API_KEY missing for speech-to-text."

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.openai_api_key)
            with file_path.open("rb") as audio_file:
                result = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=audio_file,
                )
            text = str(getattr(result, "text", "")).strip()
            if not text:
                return False, "No speech recognized."
            return True, text
        except Exception:
            return False, "Speech transcription failed."
