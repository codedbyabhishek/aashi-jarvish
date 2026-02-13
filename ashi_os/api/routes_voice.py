from pathlib import Path

from fastapi import APIRouter, Request

from ashi_os.core.models import VoiceCommandFileRequest, VoiceStartRequest

router = APIRouter(tags=["voice"])


@router.post("/voice/command-file")
def voice_command_file(payload: VoiceCommandFileRequest, request: Request) -> dict:
    pipeline = request.app.state.voice_pipeline
    orchestrator = request.app.state.orchestrator

    return pipeline.run_file(
        session_id=payload.session_id,
        file_path=Path(payload.file_path),
        orchestrator=orchestrator,
        speak_reply=payload.speak_reply,
    )


@router.post("/voice/start")
def voice_start(payload: VoiceStartRequest, request: Request) -> dict:
    runtime = request.app.state.voice_runtime
    return runtime.start(session_id=payload.session_id, speak_reply=payload.speak_reply)


@router.post("/voice/stop")
def voice_stop(request: Request) -> dict:
    runtime = request.app.state.voice_runtime
    return runtime.stop()


@router.get("/voice/status")
def voice_status(request: Request) -> dict:
    runtime = request.app.state.voice_runtime
    return runtime.status()


@router.post("/voice/mic/start")
def mic_start(request: Request) -> dict:
    mic = request.app.state.mic_runtime
    return mic.start()


@router.post("/voice/mic/stop")
def mic_stop(request: Request) -> dict:
    mic = request.app.state.mic_runtime
    return mic.stop()


@router.get("/voice/mic/status")
def mic_status(request: Request) -> dict:
    mic = request.app.state.mic_runtime
    return mic.status()
