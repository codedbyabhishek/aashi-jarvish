from .types import Intent


class IntentRouter:
    def route(self, text: str) -> Intent:
        lower = text.lower()

        if lower in {"exit", "quit"}:
            return Intent("exit")
        if lower == "help":
            return Intent("help")
        if lower == "time":
            return Intent("time")
        if lower == "date":
            return Intent("date")
        if lower == "notes":
            return Intent("notes")
        if lower.startswith("save "):
            return Intent("save_note", {"note": text[5:].strip()})

        if lower == "voices":
            return Intent("voices")
        if lower == "voice on":
            return Intent("voice_on")
        if lower == "voice off":
            return Intent("voice_off")
        if lower.startswith("voice mode "):
            return Intent("voice_mode", {"mode": text[11:].strip().lower()})
        if lower.startswith("voice "):
            return Intent("voice_set", {"voice": text[6:].strip()})

        if lower == "voicefiles":
            return Intent("voice_files")
        if lower.startswith("voicefile "):
            return Intent("voice_file_set", {"filename": text[10:].strip()})

        if lower.startswith("clonevoice "):
            parts = text.split(maxsplit=2)
            payload = {
                "filename": parts[1] if len(parts) > 1 else "",
                "name": parts[2].strip() if len(parts) == 3 else "Aashi Custom Voice",
            }
            return Intent("clone_train", payload)
        if lower == "clone status":
            return Intent("clone_status")

        if lower.startswith("listen "):
            return Intent("voice_input", {"filename": text[7:].strip()})

        if lower.startswith("open app "):
            return Intent("system_action", {"text": text})
        if lower.startswith("open web "):
            return Intent("system_action", {"text": text})
        if lower.startswith("search web "):
            return Intent("system_action", {"text": text})
        if lower.startswith("run shortcut "):
            return Intent("system_action", {"text": text})

        return Intent("chat", {"text": text})
