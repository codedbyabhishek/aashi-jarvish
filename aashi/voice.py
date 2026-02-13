import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class VoiceEngine:
    AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aiff", ".aac"}

    def __init__(self, voice_files_dir: Path) -> None:
        self.voice_files_dir = voice_files_dir

    def available_system_voices(self, limit: int = 50) -> list[str]:
        if not shutil.which("say"):
            return []

        try:
            result = subprocess.run(
                ["say", "-v", "?"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return []

            names: list[str] = []
            for line in result.stdout.splitlines():
                match = re.match(r"^(.*?)\s{2,}[a-z]{2}_[A-Z]{2}\s+#", line)
                name = match.group(1).strip() if match else ""
                if name:
                    names.append(name)
                if len(names) >= limit:
                    break
            return names
        except OSError:
            return []

    def match_system_voice(self, requested: str) -> Optional[str]:
        requested_lower = requested.lower()
        for voice in self.available_system_voices(limit=200):
            if voice.lower() == requested_lower:
                return voice
        return None

    def available_voice_files(self, limit: int = 50) -> list[str]:
        if not self.voice_files_dir.exists() or not self.voice_files_dir.is_dir():
            return []

        files: list[str] = []
        for path in sorted(self.voice_files_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in self.AUDIO_EXTENSIONS:
                files.append(path.name)
            if len(files) >= limit:
                break
        return files

    def match_voice_file(self, requested: str) -> Optional[str]:
        requested_lower = requested.lower()
        for filename in self.available_voice_files(limit=200):
            if filename.lower() == requested_lower:
                return filename
        return None

    def speak_system(self, voice_name: str, text: str) -> None:
        if not shutil.which("say"):
            return

        try:
            subprocess.run(
                ["say", "-v", voice_name, text],
                check=False,
                capture_output=True,
            )
        except OSError:
            return

    def play_file(self, filename: str) -> None:
        if not filename:
            return

        file_path = self.voice_files_dir / filename
        if not file_path.exists():
            return

        try:
            if shutil.which("afplay"):
                subprocess.run(
                    ["afplay", str(file_path)],
                    check=False,
                    capture_output=True,
                )
                return

            if shutil.which("ffplay"):
                subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", str(file_path)],
                    check=False,
                    capture_output=True,
                )
                return
        except OSError:
            return
