import datetime as dt
import re

from .types import ExecutionResult


class ToolExecutor:
    OPENAI_SETUP_URL = "https://platform.openai.com/api-keys"
    ELEVENLABS_SETUP_URL = "https://elevenlabs.io/app/settings/api-keys"

    def __init__(self, assistant) -> None:
        self.assistant = assistant

    def execute(self, action: dict) -> ExecutionResult:
        kind = action.get("kind")
        payload = action.get("payload", {})

        if kind == "exit":
            return ExecutionResult(True, self.assistant.EXIT_SIGNAL)

        if kind == "help":
            return ExecutionResult(True, self.assistant.help_text())

        if kind == "time":
            now = dt.datetime.now().strftime("%I:%M:%S %p")
            return ExecutionResult(True, f"Current time is {now}.")

        if kind == "date":
            today = dt.date.today().strftime("%A, %B %d, %Y")
            return ExecutionResult(True, f"Today's date is {today}.")

        if kind == "notes":
            notes = self.assistant.memory.notes()
            if not notes:
                return ExecutionResult(True, "No notes saved yet.")
            lines = [f"{index}. {note}" for index, note in enumerate(notes, start=1)]
            return ExecutionResult(True, "Saved notes:\n" + "\n".join(lines))

        if kind == "save_note":
            note = str(payload.get("note", "")).strip()
            if not note:
                return ExecutionResult(True, "Please provide text after 'save'.")
            self.assistant.memory.add_note(note)
            return ExecutionResult(True, "Saved.")

        if kind == "voices":
            voices = self.assistant.voice.available_system_voices(limit=30)
            if not voices:
                return ExecutionResult(True, "No system voices found on this machine.")
            return ExecutionResult(True, "Available voices:\n" + ", ".join(voices))

        if kind == "voice_on":
            self.assistant.memory.set_voice_enabled(True)
            mode = self.assistant.memory.voice_mode()
            if mode == "clone":
                clone_name = self.assistant.memory.clone_voice_name() or "(not set)"
                return ExecutionResult(True, f"Voice output enabled in clone mode with '{clone_name}'.")
            if mode == "file":
                file_name = self.assistant.memory.voice_file() or "(not set)"
                return ExecutionResult(True, f"Voice output enabled in file mode with '{file_name}'.")
            return ExecutionResult(True, f"Voice output enabled with '{self.assistant.memory.voice_name()}'.")

        if kind == "voice_off":
            self.assistant.memory.set_voice_enabled(False)
            return ExecutionResult(True, "Voice output disabled.")

        if kind == "voice_mode":
            mode = str(payload.get("mode", "")).strip().lower()
            if mode not in {"system", "file", "clone"}:
                return ExecutionResult(True, "Use: voice mode system OR voice mode file OR voice mode clone")
            if mode == "clone" and not self.assistant.memory.clone_voice_id():
                return ExecutionResult(True, "No clone voice configured. Run: clonevoice <filename> [name]")
            self.assistant.memory.set_voice_mode(mode)
            return ExecutionResult(True, f"Voice mode set to '{mode}'.")

        if kind == "voice_set":
            requested = str(payload.get("voice", "")).strip()
            if not requested:
                return ExecutionResult(True, "Use: voice <name>")
            matched = self.assistant.voice.match_system_voice(requested)
            if not matched:
                return ExecutionResult(True, "Voice not found. Type 'voices' to see available names.")
            self.assistant.memory.set_voice_name(matched)
            return ExecutionResult(True, f"Voice set to '{matched}'. Use 'voice on' to hear responses.")

        if kind == "voice_files":
            files = self.assistant.voice.available_voice_files(limit=50)
            if not files:
                return ExecutionResult(True, "No audio files found in ./save. Add .wav or .mp3 files there.")
            return ExecutionResult(True, "Voice files in ./save:\n" + ", ".join(files))

        if kind == "voice_file_set":
            filename = str(payload.get("filename", "")).strip()
            if not filename:
                return ExecutionResult(True, "Use: voicefile <filename>")
            matched = self.assistant.voice.match_voice_file(filename)
            if not matched:
                return ExecutionResult(True, "File not found in ./save. Type 'voicefiles' to see available files.")
            self.assistant.memory.set_voice_file(matched)
            self.assistant.memory.set_voice_mode("file")
            return ExecutionResult(True, f"Voice file set to '{matched}'. Mode switched to 'file'.")

        if kind == "clone_train":
            filename = str(payload.get("filename", "")).strip()
            clone_name = str(payload.get("name", "Aashi Custom Voice")).strip() or "Aashi Custom Voice"
            if not filename:
                return ExecutionResult(True, "Use: clonevoice <filename> [name]")
            if not self.assistant.clone_voice.has_api_key():
                opened, _ = self.assistant.system_control.open_url(self.ELEVENLABS_SETUP_URL)
                if opened:
                    return ExecutionResult(
                        True,
                        "ELEVENLABS_API_KEY is missing. Opened ElevenLabs API key page. "
                        "Create key, then run: export ELEVENLABS_API_KEY='your_key'",
                    )
                return ExecutionResult(
                    True,
                    "ELEVENLABS_API_KEY is missing. Open this page and create key: "
                    f"{self.ELEVENLABS_SETUP_URL}",
                )
            ok, voice_id, message = self.assistant.clone_voice.clone_from_file(filename, clone_name)
            if not ok:
                return ExecutionResult(True, f"Clone failed: {message}")
            self.assistant.memory.set_clone_voice(voice_id, clone_name)
            self.assistant.memory.set_voice_mode("clone")
            return ExecutionResult(True, f"Clone ready as '{clone_name}'. Voice mode switched to 'clone'.")

        if kind == "clone_status":
            clone_name = self.assistant.memory.clone_voice_name() or "(not configured)"
            clone_id = self.assistant.memory.clone_voice_id()
            if clone_id:
                return ExecutionResult(True, f"Clone voice ready: '{clone_name}' (id: {clone_id[:8]}...).")
            return ExecutionResult(True, "Clone voice not configured. Use: clonevoice <filename> [name]")

        if kind == "voice_input":
            filename = str(payload.get("filename", "")).strip()
            if not filename:
                return ExecutionResult(True, "Use: listen <filename>")
            if not self.assistant.voice_input.has_api_key():
                opened, _ = self.assistant.system_control.open_url(self.OPENAI_SETUP_URL)
                if opened:
                    return ExecutionResult(
                        True,
                        "OPENAI_API_KEY is missing. Opened OpenAI API key page. "
                        "Create key, then run: export OPENAI_API_KEY='your_key'",
                    )
                return ExecutionResult(
                    True,
                    "OPENAI_API_KEY is missing. Open this page and create key: "
                    f"{self.OPENAI_SETUP_URL}",
                )
            ok, transcript = self.assistant.voice_input.transcribe_file(filename)
            if not ok:
                return ExecutionResult(True, f"Voice input failed: {transcript}")
            command_text = transcript.strip()
            if self.assistant.memory.wake_enabled():
                wake_phrase = self.assistant.memory.wake_phrase().lower()
                lower = command_text.lower()
                if wake_phrase not in lower:
                    return ExecutionResult(
                        True,
                        f"Heard: {transcript}\nWake phrase not detected. Say '{self.assistant.memory.wake_phrase()}' first.",
                    )
                split = re.split(re.escape(wake_phrase), lower, maxsplit=1)
                if len(split) == 2:
                    suffix = split[1].strip(" ,.!?;:-")
                    if not suffix:
                        return ExecutionResult(True, f"Heard: {transcript}\nListening. Give a command after wake phrase.")
                    start_index = lower.find(wake_phrase) + len(wake_phrase)
                    command_text = transcript[start_index:].strip(" ,.!?;:-")
            nested_reply = self.assistant.handle(command_text)
            if nested_reply == self.assistant.EXIT_SIGNAL:
                return ExecutionResult(True, f"Heard: {transcript}\nAashi: Goodbye.")
            return ExecutionResult(True, f"Heard: {transcript}\nAashi: {nested_reply}")

        if kind == "wake_on":
            self.assistant.memory.set_wake_enabled(True)
            return ExecutionResult(True, f"Wake activation enabled. Phrase: '{self.assistant.memory.wake_phrase()}'.")

        if kind == "wake_off":
            self.assistant.memory.set_wake_enabled(False)
            return ExecutionResult(True, "Wake activation disabled for voice input.")

        if kind == "wake_status":
            state = "enabled" if self.assistant.memory.wake_enabled() else "disabled"
            return ExecutionResult(True, f"Wake status: {state}. Phrase: '{self.assistant.memory.wake_phrase()}'.")

        if kind == "wake_phrase":
            phrase = str(payload.get("phrase", "")).strip()
            if not phrase:
                return ExecutionResult(True, "Use: wake phrase <text>")
            self.assistant.memory.set_wake_phrase(phrase.lower())
            self.assistant.memory.set_wake_enabled(True)
            return ExecutionResult(True, f"Wake phrase set to '{self.assistant.memory.wake_phrase()}'.")

        if kind == "setup_openai":
            opened, _ = self.assistant.system_control.open_url(self.OPENAI_SETUP_URL)
            if opened:
                return ExecutionResult(
                    True,
                    "Opened OpenAI API key page. Create key and run: export OPENAI_API_KEY='your_key'",
                )
            return ExecutionResult(True, f"Open this URL to create key: {self.OPENAI_SETUP_URL}")

        if kind == "setup_elevenlabs":
            opened, _ = self.assistant.system_control.open_url(self.ELEVENLABS_SETUP_URL)
            if opened:
                return ExecutionResult(
                    True,
                    "Opened ElevenLabs API key page. Create key and run: export ELEVENLABS_API_KEY='your_key'",
                )
            return ExecutionResult(True, f"Open this URL to create key: {self.ELEVENLABS_SETUP_URL}")

        if kind == "setup_status":
            openai_ready = "set" if self.assistant.voice_input.has_api_key() else "missing"
            elevenlabs_ready = "set" if self.assistant.clone_voice.has_api_key() else "missing"
            return ExecutionResult(
                True,
                f"Setup status: OPENAI_API_KEY={openai_ready}, ELEVENLABS_API_KEY={elevenlabs_ready}.",
            )

        if kind == "system_action":
            ok, message = self.assistant.system_control.try_natural_action(str(payload.get("text", "")))
            if ok or message:
                return ExecutionResult(True, message)
            return ExecutionResult(True, "I could not understand the system action.")

        if kind == "chat":
            text = str(payload.get("text", "")).strip()
            reply = self.assistant.brain.think(self.assistant.router.route(text))
            return ExecutionResult(True, reply)

        return ExecutionResult(False, "Unknown action.")
