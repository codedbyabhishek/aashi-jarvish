import datetime as dt
import os
from typing import Optional

from .ai import AIResponder
from .config import AppConfig
from .memory import MemoryStore
from .voice import VoiceEngine


class AashiAssistant:
    EXIT_SIGNAL = "EXIT"

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        memory: Optional[MemoryStore] = None,
        voice: Optional[VoiceEngine] = None,
        ai: Optional[AIResponder] = None,
    ) -> None:
        self.config = config or AppConfig.from_env()
        self.memory = memory or MemoryStore(self.config.memory_file)
        self.voice = voice or VoiceEngine(self.config.voice_files_dir)
        self.ai = ai or AIResponder(
            model=self.config.openai_model,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

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

        command_reply = self._handle_command(text)
        if command_reply is not None:
            return command_reply

        ai_reply = self.ai.reply(text)
        if ai_reply:
            return ai_reply

        return self._fallback_reply(text)

    def _handle_command(self, text: str) -> Optional[str]:
        lower = text.lower()

        if lower in {"exit", "quit"}:
            return self.EXIT_SIGNAL

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
            lines = [f"{index}. {note}" for index, note in enumerate(notes, start=1)]
            return "Saved notes:\n" + "\n".join(lines)

        if lower.startswith("save "):
            return self._handle_save_note(text)

        if lower == "voices":
            voices = self.voice.available_system_voices(limit=30)
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

        if lower.startswith("voice mode "):
            return self._handle_voice_mode(text)

        if lower.startswith("voice "):
            return self._handle_system_voice(text)

        if lower == "voicefiles":
            files = self.voice.available_voice_files(limit=50)
            if not files:
                return "No audio files found in ./save. Add .wav or .mp3 files there."
            return "Voice files in ./save:\n" + ", ".join(files)

        if lower.startswith("voicefile "):
            return self._handle_voice_file(text)

        return None

    def _handle_save_note(self, text: str) -> str:
        note = text[5:].strip()
        if not note:
            return "Please provide text after 'save'."
        self.memory.add_note(note)
        return "Saved."

    def _handle_voice_mode(self, text: str) -> str:
        mode = text[11:].strip().lower()
        if mode not in {"system", "file"}:
            return "Use: voice mode system OR voice mode file"
        self.memory.set_voice_mode(mode)
        return f"Voice mode set to '{mode}'."

    def _handle_system_voice(self, text: str) -> str:
        requested = text[6:].strip()
        if not requested:
            return "Use: voice <name>"

        matched = self.voice.match_system_voice(requested)
        if not matched:
            return "Voice not found. Type 'voices' to see available names."

        self.memory.set_voice_name(matched)
        return f"Voice set to '{matched}'. Use 'voice on' to hear responses."

    def _handle_voice_file(self, text: str) -> str:
        requested_file = text[10:].strip()
        if not requested_file:
            return "Use: voicefile <filename>"

        matched_file = self.voice.match_voice_file(requested_file)
        if not matched_file:
            return "File not found in ./save. Type 'voicefiles' to see available files."

        self.memory.set_voice_file(matched_file)
        self.memory.set_voice_mode("file")
        return f"Voice file set to '{matched_file}'. Mode switched to 'file'."

    def speak(self, text: str) -> None:
        if not self.memory.voice_enabled():
            return

        if self.memory.voice_mode() == "file":
            self.voice.play_file(self.memory.voice_file())
            return

        self.voice.speak_system(self.memory.voice_name(), text)

    def _fallback_reply(self, prompt: str) -> str:
        return (
            "I can help with tasks, reminders, notes, and quick questions. "
            "For smarter answers, set OPENAI_API_KEY. "
            f"You said: {prompt}"
        )
