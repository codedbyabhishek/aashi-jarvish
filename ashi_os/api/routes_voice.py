from pathlib import Path

from fastapi import APIRouter, Request

from ashi_os.core.models import VoiceCommandFileRequest
from ashi_os.voice.listener import VoiceCommandPipeline
from ashi_os.voice.stt import SpeechToTextService
from ashi_os.voice.tts import TextToSpeechService

router = APIRouter(tags=["voice"])


@router.post("/voice/command-file")
def voice_command_file(payload: VoiceCommandFileRequest, request: Request) -> dict:
    settings = request.app.state.settings
    orchestrator = request.app.state.orchestrator

    stt = SpeechToTextService(settings.openai_api_key)
    tts = TextToSpeechService()
    pipeline = VoiceCommandPipeline(stt=stt, tts=tts, wake_phrase="hey aashi")

    return pipeline.run_file(
        session_id=payload.session_id,
        file_path=Path(payload.file_path),
        orchestrator=orchestrator,
        speak_reply=payload.speak_reply,
    )
