from pathlib import Path

from ashi_os.brain.orchestrator import Orchestrator
from ashi_os.brain.planning import RiskEvaluator, StrategicPlanner
from ashi_os.brain.context_manager import ContextManager
from ashi_os.core.config import Settings
from ashi_os.logging.audit_log import AuditLogger
from ashi_os.memory.memory_service import MemoryService


class StubRouter:
    def generate(self, prompt: str) -> tuple[str, str, str]:
        return ("stub-reply", "stub", "stub-model")


def make_settings() -> Settings:
    return Settings(
        env="test",
        default_llm="ollama",
        fallback_llm="openai",
        ollama_model="model",
        openai_model="model",
        openai_api_key="",
        chroma_dir=Path("./data/chroma"),
        sqlite_path=Path("./data/state.db"),
        log_dir=Path("./data/logs"),
        max_context_tokens=8000,
        memory_top_k=3,
        memory_on_chat=False,
        wake_phrase="hey aashi",
        default_tts_voice="Samantha",
        voice_inbox_dir=Path("./data/voice/inbox"),
        voice_processed_dir=Path("./data/voice/processed"),
        voice_poll_interval_sec=1.0,
        mic_sample_rate=16000,
        mic_chunk_seconds=2.0,
        mic_channels=1,
        mic_device_index=None,
    )


def test_planner_decomposes_multistep_request() -> None:
    planner = StrategicPlanner()
    plan = planner.build_plan("open browser and search weather then summarize")
    assert len(plan.steps) >= 2
    assert plan.objective.startswith("open browser")


def test_risk_evaluator_high_requires_confirmation() -> None:
    planner = StrategicPlanner()
    risk = RiskEvaluator().evaluate("delete all files and shutdown laptop", planner.build_plan("delete files"))
    assert risk.level == "high"
    assert risk.confirmation_required is True


def test_orchestrator_confirmation_roundtrip() -> None:
    settings = make_settings()
    memory = MemoryService(settings)
    context = ContextManager(settings, memory)
    orchestrator = Orchestrator(
        router=StubRouter(),
        context_manager=context,
        memory=memory,
        audit=AuditLogger(Path("./data/logs")),
        memory_on_chat=False,
    )

    blocked = orchestrator.chat("s-confirm", "delete project files")
    assert blocked["confirmation_required"] is True
    token = blocked["confirmation_token"]
    assert token

    approved = orchestrator.chat("s-confirm", f"confirm {token}")
    assert approved["confirmation_required"] is False
    assert approved["reply"] == "stub-reply"
