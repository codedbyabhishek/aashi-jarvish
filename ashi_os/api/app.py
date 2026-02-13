from pathlib import Path

from fastapi import FastAPI

from ashi_os.api.routes_admin import router as admin_router
from ashi_os.api.routes_agents import router as agents_router
from ashi_os.api.routes_chat import router as chat_router
from ashi_os.api.routes_tools import router as tools_router
from ashi_os.api.routes_voice import router as voice_router
from ashi_os.agents.coordinator import AgentCoordinator
from ashi_os.agents.execution_agent import ExecutionAgent
from ashi_os.agents.memory_agent import MemoryAgent
from ashi_os.agents.research_agent import ResearchAgent
from ashi_os.agents.supervisor_agent import SupervisorAgent
from ashi_os.agents.validation_agent import ValidationAgent
from ashi_os.brain.confirmation import ConfirmationManager
from ashi_os.brain.context_manager import ContextManager
from ashi_os.brain.llm_router import LLMRouter
from ashi_os.brain.orchestrator import Orchestrator
from ashi_os.brain.planning import RiskEvaluator, StrategicPlanner
from ashi_os.core.config import get_settings
from ashi_os.logging.audit_log import AuditLogger
from ashi_os.logging.logger import configure_logging
from ashi_os.memory.memory_service import MemoryService
from ashi_os.voice.continuous import ContinuousVoiceRuntime
from ashi_os.voice.listener import VoiceCommandPipeline
from ashi_os.voice.mic_capture import MicrophoneCaptureRuntime
from ashi_os.voice.stt import SpeechToTextService
from ashi_os.voice.tts import TextToSpeechService
from ashi_os.tools.executor import ToolExecutor


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    memory = MemoryService(settings)
    audit = AuditLogger(settings.log_dir)
    router = LLMRouter(settings)
    context = ContextManager(settings, memory)
    orchestrator = Orchestrator(
        router=router,
        context_manager=context,
        memory=memory,
        audit=audit,
        memory_on_chat=settings.memory_on_chat,
    )

    stt = SpeechToTextService(settings.openai_api_key)
    tts = TextToSpeechService()
    voice_pipeline = VoiceCommandPipeline(
        stt=stt,
        tts=tts,
        wake_phrase=settings.wake_phrase,
        default_voice=settings.default_tts_voice,
    )
    voice_runtime = ContinuousVoiceRuntime(
        pipeline=voice_pipeline,
        orchestrator=orchestrator,
        inbox_dir=settings.voice_inbox_dir,
        processed_dir=settings.voice_processed_dir,
        poll_interval_sec=settings.voice_poll_interval_sec,
    )
    mic_runtime = MicrophoneCaptureRuntime(
        inbox_dir=settings.voice_inbox_dir,
        sample_rate=settings.mic_sample_rate,
        chunk_seconds=settings.mic_chunk_seconds,
        channels=settings.mic_channels,
        device=settings.mic_device_index,
    )
    tool_executor = ToolExecutor(
        workspace_root=Path.cwd(),
        sqlite_path=settings.sqlite_path,
        audit=audit,
    )
    agent_coordinator = AgentCoordinator(
        research=ResearchAgent(memory=memory, top_k=settings.memory_top_k),
        execution=ExecutionAgent(tool_executor=tool_executor),
        validation=ValidationAgent(),
        memory_agent=MemoryAgent(memory=memory),
        supervisor=SupervisorAgent(),
        planner=StrategicPlanner(),
        risk_evaluator=RiskEvaluator(),
        confirmation=ConfirmationManager(),
        audit=audit,
    )

    app = FastAPI(title="ASHI OS", version="0.1.0")
    app.state.settings = settings
    app.state.memory = memory
    app.state.audit = audit
    app.state.orchestrator = orchestrator
    app.state.voice_pipeline = voice_pipeline
    app.state.voice_runtime = voice_runtime
    app.state.mic_runtime = mic_runtime
    app.state.tool_executor = tool_executor
    app.state.agent_coordinator = agent_coordinator

    app.include_router(admin_router)
    app.include_router(agents_router)
    app.include_router(chat_router)
    app.include_router(voice_router)
    app.include_router(tools_router)

    @app.on_event("shutdown")
    def _shutdown_runtimes() -> None:
        app.state.voice_runtime.stop()
        app.state.mic_runtime.stop()

    return app


app = create_app()
