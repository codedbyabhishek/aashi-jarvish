from pathlib import Path

from ashi_os.logging.audit_log import AuditLogger
from ashi_os.tools.executor import ToolExecutor


def test_filesystem_write_and_read(tmp_path: Path) -> None:
    sqlite_path = tmp_path / "state.db"
    executor = ToolExecutor(
        workspace_root=tmp_path,
        sqlite_path=sqlite_path,
        audit=AuditLogger(tmp_path / "logs"),
    )

    write = executor.execute(
        session_id="s1",
        tool="filesystem",
        action="write",
        params={"path": "notes/test.txt", "content": "hello"},
    )
    assert write["ok"] is True

    read = executor.execute(
        session_id="s1",
        tool="filesystem",
        action="read",
        params={"path": "notes/test.txt"},
    )
    assert read["ok"] is True
    assert read["content"] == "hello"


def test_scheduler_create_and_run_due(tmp_path: Path) -> None:
    sqlite_path = tmp_path / "state.db"
    executor = ToolExecutor(
        workspace_root=tmp_path,
        sqlite_path=sqlite_path,
        audit=AuditLogger(tmp_path / "logs"),
    )

    created = executor.execute(
        session_id="sched",
        tool="scheduler",
        action="create",
        params={
            "run_at": "1970-01-01T00:00:00+00:00",
            "tool": "filesystem",
            "action": "write",
            "params": {"path": "scheduled.txt", "content": "done"},
        },
        confirm=True,
    )
    assert created["ok"] is True

    ran = executor.execute(
        session_id="sched",
        tool="scheduler",
        action="run_due",
        params={},
        confirm=True,
    )
    assert ran["ok"] is True
    assert ran["processed"] >= 1

    out = (tmp_path / "scheduled.txt").read_text(encoding="utf-8")
    assert out == "done"
