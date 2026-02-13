from pathlib import Path

from ashi_os.voice.stt import SpeechToTextService
from ashi_os.voice.tts import TextToSpeechService
from ashi_os.voice.wake_word import detect_wake_phrase


class VoiceCommandPipeline:
    def __init__(
        self,
        stt: SpeechToTextService,
        tts: TextToSpeechService,
        wake_phrase: str,
        default_voice: str = "Samantha",
    ) -> None:
        self.stt = stt
        self.tts = tts
        self.wake_phrase = wake_phrase
        self.default_voice = default_voice

    def run_file(self, session_id: str, file_path: Path, orchestrator, speak_reply: bool) -> dict:
        ok, transcript = self.stt.transcribe_file(file_path)
        if not ok:
            return {
                "ok": False,
                "session_id": session_id,
                "transcript": "",
                "command": "",
                "reply": transcript,
            }

        wake, command = detect_wake_phrase(transcript, self.wake_phrase)
        if not wake:
            return {
                "ok": False,
                "session_id": session_id,
                "transcript": transcript,
                "command": "",
                "reply": f"Wake phrase '{self.wake_phrase}' not detected.",
            }

        if not command:
            return {
                "ok": False,
                "session_id": session_id,
                "transcript": transcript,
                "command": "",
                "reply": "Wake phrase heard. Waiting for command.",
            }

        reply, provider, model = orchestrator.chat(session_id=session_id, user_message=command)
        if speak_reply:
            self.tts.speak(reply, self.default_voice)

        return {
            "ok": True,
            "session_id": session_id,
            "transcript": transcript,
            "command": command,
            "reply": reply,
            "provider": provider,
            "model": model,
        }
