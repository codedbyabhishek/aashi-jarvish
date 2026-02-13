import shutil
import subprocess


class TextToSpeechService:
    def speak(self, text: str, voice_name: str = "Samantha") -> bool:
        if not text.strip():
            return False
        if not shutil.which("say"):
            return False
        try:
            result = subprocess.run(["say", "-v", voice_name, text], capture_output=True, check=False)
            return result.returncode == 0
        except OSError:
            return False
