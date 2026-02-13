import datetime as dt
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .memory import MemoryStore


class AashiAssistant:
    AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aiff", ".aac"}

    def __init__(self, memory: Optional[MemoryStore] = None) -> None:
        self.memory = memory or MemoryStore()
        self._client = None
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._voice_files_dir = Path("save")

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=api_key)
            except Exception:
                self._client = None

    def greet(self) -> str:
        return (
            "Hi, I am Aashi. Your personal Jarvish assistant is online. "
            "Type 'help' to see what I can do."
        )

    def help_text(self) -> str:
        return (
            "Commands: help, time, date, notes, save <text>, voices, voice <name>, voice on, voice off,\n"
            "voice mode <system|file>, voicefiles, voicefile <filename>, exit\n"
            "You can also ask normal questions."
        )

    def handle(self, user_input: str) -> str:
        text = user_input.strip()
        if not text:
            return "Say something and I will help."

        lower = text.lower()

        if lower in {"exit", "quit"}:
            return "EXIT"

        if lower == "help":
            return self.help_text()

        if lower == "time":
            now = dt.datetime.now().strftime("%I:%M:%S %p")
            return f"Current time is {now}."

        if lower == "date":
            today = dt.date.today().strftime("%A, %B %d, %Y")
            return f"Today's date is {today}."

        if lower == "notes":
            notes = self.memory.notes()
            if not notes:
                return "No notes saved yet."
            lines = [f"{idx}. {note}" for idx, note in enumerate(notes, start=1)]
            return "Saved notes:\n" + "\n".join(lines)

        if lower.startswith("save "):
            note = text[5:].strip()
            if not note:
                return "Please provide text after 'save'."
            self.memory.add_note(note)
            return "Saved."

        if lower == "voices":
            voices = self.available_voices(limit=20)
            if not voices:
                return "No system voices found on this machine."
            return "Available voices:\n" + ", ".join(voices)

        if lower == "voice on":
            self.memory.set_voice_enabled(True)
            if self.memory.voice_mode() == "file":
                file_name = self.memory.voice_file() or "(not set)"
                return f"Voice output enabled in file mode with '{file_name}'."
            return f"Voice output enabled with '{self.memory.voice_name()}'."

        if lower == "voice off":
            self.memory.set_voice_enabled(False)
            return "Voice output disabled."

        if lower.startswith("voice "):
            if lower.startswith("voice mode "):
                mode = text[11:].strip().lower()
                if mode not in {"system", "file"}:
                    return "Use: voice mode system OR voice mode file"
                self.memory.set_voice_mode(mode)
                return f"Voice mode set to '{mode}'."
            requested = text[6:].strip()
            if not requested:
                return "Use: voice <name>"
            matched = self.match_voice_name(requested)
            if not matched:
                return "Voice not found. Type 'voices' to see available names."
            self.memory.set_voice_name(matched)
            return f"Voice set to '{matched}'. Use 'voice on' to hear responses."

        if lower == "voicefiles":
            files = self.available_voice_files(limit=50)
            if not files:
                return "No audio files found in ./save. Add .wav or .mp3 files there."
            return "Voice files in ./save:\n" + ", ".join(files)

        if lower.startswith("voicefile "):
            requested_file = text[10:].strip()
            if not requested_file:
                return "Use: voicefile <filename>"
            matched_file = self.match_voice_file(requested_file)
            if not matched_file:
                return "File not found in ./save. Type 'voicefiles' to see available files."
            self.memory.set_voice_file(matched_file)
            self.memory.set_voice_mode("file")
            return f"Voice file set to '{matched_file}'. Mode switched to 'file'."

        ai_reply = self._ask_openai(text)
        if ai_reply:
            return ai_reply

        return self._fallback_reply(text)

    def _ask_openai(self, prompt: str) -> Optional[str]:
        if not self._client:
            return None

        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are Aashi, a concise personal AI assistant. "
                            "Be practical, clear, and helpful."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return response.output_text.strip()
        except Exception:
            return None

    def _fallback_reply(self, prompt: str) -> str:
        return (
            "I can help with tasks, reminders, notes, and quick questions. "
            "For smarter answers, set OPENAI_API_KEY. "
            f"You said: {prompt}"
        )

    def available_voices(self, limit: int = 50) -> list[str]:
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

    def match_voice_name(self, requested: str) -> Optional[str]:
        requested_lower = requested.lower()
        for voice in self.available_voices(limit=200):
            if voice.lower() == requested_lower:
                return voice
        return None

    def speak(self, text: str) -> None:
        if not self.memory.voice_enabled():
            return
        if self.memory.voice_mode() == "file":
            self._play_voice_file()
            return
        if not shutil.which("say"):
            return
        voice = self.memory.voice_name()
        try:
            subprocess.run(
                ["say", "-v", voice, text],
                check=False,
                capture_output=True,
            )
        except OSError:
            return

    def available_voice_files(self, limit: int = 50) -> list[str]:
        if not self._voice_files_dir.exists() or not self._voice_files_dir.is_dir():
            return []
        files: list[str] = []
        for path in sorted(self._voice_files_dir.iterdir()):
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

    def _play_voice_file(self) -> None:
        filename = self.memory.voice_file()
        if not filename:
            return
        file_path = self._voice_files_dir / filename
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
