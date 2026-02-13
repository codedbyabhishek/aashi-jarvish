from pathlib import Path

from ashi_os.agents.coordinator import AgentCoordinator
from ashi_os.agents.execution_agent import ExecutionAgent
from ashi_os.agents.memory_agent import MemoryAgent
from ashi_os.agents.research_agent import ResearchAgent
from ashi_os.agents.supervisor_agent import SupervisorAgent
from ashi_os.agents.validation_agent import ValidationAgent
from ashi_os.brain.confirmation import ConfirmationManager
from ashi_os.brain.planning import RiskEvaluator, StrategicPlanner
from ashi_os.core.config import Settings
from ashi_os.logging.audit_log import AuditLogger
from ashi_os.memory.memory_service import MemoryService
from ashi_os.tools.executor import ToolExecutor


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        env="test",
        default_llm="ollama",
        fallback_llm="openai",
        ollama_model="model",
        openai_model="model",
        openai_api_key="",
        chroma_dir=tmp_path / "chroma",
        sqlite_path=tmp_path / "state.db",
        log_dir=tmp_path / "logs",
        max_context_tokens=8000,
        memory_top_k=3,
        memory_on_chat=False,
        wake_phrase="hey aashi",
        default_tts_voice="Samantha",
        voice_inbox_dir=tmp_path / "voice" / "inbox",
        voice_processed_dir=tmp_path / "voice" / "processed",
        voice_poll_interval_sec=1.0,
        mic_sample_rate=16000,
        mic_chunk_seconds=2.0,
        mic_channels=1,
        mic_device_index=None,
    )


def _coordinator(tmp_path: Path) -> AgentCoordinator:
    settings = _settings(tmp_path)
    memory = MemoryService(settings)
    audit = AuditLogger(settings.log_dir)
    tools = ToolExecutor(workspace_root=tmp_path, sqlite_path=settings.sqlite_path, audit=audit)
    return AgentCoordinator(
        research=ResearchAgent(memory=memory, top_k=3),
        execution=ExecutionAgent(tool_executor=tools),
        validation=ValidationAgent(),
        memory_agent=MemoryAgent(memory=memory),
        supervisor=SupervisorAgent(),
        planner=StrategicPlanner(),
        risk_evaluator=RiskEvaluator(),
        confirmation=ConfirmationManager(),
        audit=audit,
    )


def test_agents_confirmation_required_for_high_risk(tmp_path: Path) -> None:
    coordinator = _coordinator(tmp_path)
    result = coordinator.run(
        session_id="agent-s1",
        objective="delete all files in project",
        auto_execute=True,
    )
    assert result["confirmation_required"] is True
    assert result["confirmation_token"]


def test_agents_auto_execute_write_file_after_confirmation(tmp_path: Path) -> None:
    coordinator = _coordinator(tmp_path)

    first = coordinator.run(
        session_id="agent-s2",
        objective="delete old logs and write file notes.txt::done",
        auto_execute=True,
    )
    token = first["confirmation_token"]
    assert token

    second = coordinator.run(
        session_id="agent-s2",
        objective="ignored",
        auto_execute=True,
        confirm_token=token,
    )

    assert second["confirmation_required"] is False
    assert isinstance(second["execution_results"], list)
