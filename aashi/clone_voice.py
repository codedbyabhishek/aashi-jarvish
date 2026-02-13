import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class CloneVoiceEngine:
    def __init__(self, voice_files_dir: Path, api_key: Optional[str]) -> None:
        self.voice_files_dir = voice_files_dir
        self.api_key = api_key or ""
        self._cache_dir = Path(tempfile.gettempdir()) / "aashi_audio"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def clone_from_file(self, filename: str, clone_name: str) -> tuple[bool, str, str]:
        if not self.api_key:
            return False, "", "Set ELEVENLABS_API_KEY first."

        if not shutil.which("curl"):
            return False, "", "curl is not available on this system."

        file_path = self.voice_files_dir / filename
        if not file_path.exists() or not file_path.is_file():
            return False, "", "Voice file not found in ./save."

        cmd = [
            "curl",
            "-sS",
            "-X",
            "POST",
            "https://api.elevenlabs.io/v1/voices/add",
            "-H",
            f"xi-api-key: {self.api_key}",
            "-F",
            f"name={clone_name}",
            "-F",
            f"files[]=@{str(file_path)}",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except OSError:
            return False, "", "Failed to start curl for voice cloning."

        if result.returncode != 0:
            return False, "", "Voice cloning request failed."

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return False, "", "Invalid response from voice cloning service."

        voice_id = str(payload.get("voice_id", "")).strip()
        if not voice_id:
            detail = payload.get("detail")
            if isinstance(detail, dict):
                msg = str(detail.get("message", "Voice clone failed."))
            else:
                msg = "Voice clone failed."
            return False, "", msg

        return True, voice_id, "Voice cloned successfully."

    def speak(self, text: str, voice_id: str) -> tuple[bool, str]:
        if not self.api_key:
            return False, "Set ELEVENLABS_API_KEY first."

        if not voice_id:
            return False, "No cloned voice configured."

        if not shutil.which("curl"):
            return False, "curl is not available on this system."

        output_file = self._cache_dir / "clone_tts.mp3"
        payload = json.dumps(
            {
                "text": text[:450],
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.85,
                },
            }
        )

        cmd = [
            "curl",
            "-sS",
            "-X",
            "POST",
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            "-H",
            f"xi-api-key: {self.api_key}",
            "-H",
            "Content-Type: application/json",
            "-d",
            payload,
            "--output",
            str(output_file),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except OSError:
            return False, "Failed to start TTS request."

        if result.returncode != 0 or not output_file.exists() or output_file.stat().st_size == 0:
            return False, "Failed generating cloned voice audio."

        try:
            if shutil.which("afplay"):
                subprocess.run(["afplay", str(output_file)], capture_output=True, check=False)
                return True, ""
            if shutil.which("ffplay"):
                subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", str(output_file)],
                    capture_output=True,
                    check=False,
                )
                return True, ""
        except OSError:
            return False, "Audio playback failed."

        return False, "No audio player found (afplay/ffplay)."
