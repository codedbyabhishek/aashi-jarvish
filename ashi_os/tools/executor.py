from datetime import UTC, datetime
from pathlib import Path

from ashi_os.core.security import is_destructive_command
from ashi_os.logging.audit_log import AuditLogger
from ashi_os.tools.browser import BrowserModule
from ashi_os.tools.code_runner import CodeRunnerModule
from ashi_os.tools.email_module import EmailModule
from ashi_os.tools.filesystem import FileSystemModule
from ashi_os.tools.scheduler import SchedulerStore
from ashi_os.tools.system_control import SystemControlModule


class ToolExecutor:
    def __init__(self, workspace_root: Path, sqlite_path: Path, audit: AuditLogger) -> None:
        self.workspace_root = workspace_root
        self.audit = audit
        self.files = FileSystemModule(workspace_root)
        self.system = SystemControlModule()
        self.browser = BrowserModule()
        self.code = CodeRunnerModule(workspace_root)
        self.email = EmailModule(workspace_root / "data" / "email_queue.json")
        self.scheduler = SchedulerStore(sqlite_path)

    def catalog(self) -> dict:
        return {
            "system": ["open_app", "run_shortcut"],
            "filesystem": ["list", "read", "write", "append", "mkdir", "delete"],
            "browser": ["open_url", "search_web"],
            "code": ["run"],
            "email": ["queue", "list"],
            "scheduler": ["create", "list", "run_due"],
        }

    def execute(self, session_id: str, tool: str, action: str, params: dict, confirm: bool = False) -> dict:
        if tool == "filesystem" and action == "delete" and not confirm:
            return {"ok": False, "message": "Deletion requires confirm=true.", "risk": "elevated"}
        if tool == "code" and action == "run":
            command = str(params.get("command", ""))
            if is_destructive_command(command) and not confirm:
                return {"ok": False, "message": "Risk level elevated. Confirmation required.", "risk": "elevated"}

        try:
            result = self._execute_inner(session_id=session_id, tool=tool, action=action, params=params, confirm=confirm)
        except PermissionError as exc:
            result = {"ok": False, "message": str(exc)}
        except Exception as exc:  # pragma: no cover
            result = {"ok": False, "message": f"Unhandled tool failure: {exc}"}

        self.audit.write(
            "tool.executed",
            {
                "session_id": session_id,
                "tool": tool,
                "action": action,
                "params": params,
                "ok": bool(result.get("ok")),
            },
        )
        return result

    def run_due_jobs(self) -> dict:
        jobs = self.scheduler.due_jobs()
        ran = []
        failed = []

        for job in jobs:
            payload = job.get("payload", {})
            result = self.execute(
                session_id=job["session_id"],
                tool=str(payload.get("tool", "")),
                action=str(payload.get("action", "")),
                params=dict(payload.get("params", {})),
                confirm=bool(payload.get("confirm", False)),
            )
            if result.get("ok"):
                self.scheduler.mark_job(job["id"], "done")
                ran.append({"id": job["id"], "result": result})
            else:
                self.scheduler.mark_job(job["id"], "failed")
                failed.append({"id": job["id"], "result": result})

        return {"ok": True, "processed": len(jobs), "ran": ran, "failed": failed}

    def _execute_inner(self, session_id: str, tool: str, action: str, params: dict, confirm: bool) -> dict:
        if tool == "system":
            if action == "open_app":
                return self.system.open_app(str(params.get("app_name", "")))
            if action == "run_shortcut":
                return self.system.run_shortcut(str(params.get("shortcut_name", "")))

        if tool == "filesystem":
            if action == "list":
                return self.files.list_dir(str(params.get("path", ".")))
            if action == "read":
                return self.files.read_file(str(params.get("path", "")), int(params.get("max_chars", 20000)))
            if action == "write":
                return self.files.write_file(str(params.get("path", "")), str(params.get("content", "")), append=False)
            if action == "append":
                return self.files.write_file(str(params.get("path", "")), str(params.get("content", "")), append=True)
            if action == "mkdir":
                return self.files.mkdir(str(params.get("path", "")))
            if action == "delete":
                if not confirm:
                    return {"ok": False, "message": "Deletion requires confirm=true."}
                return self.files.delete_path(str(params.get("path", "")))

        if tool == "browser":
            if action == "open_url":
                return self.browser.open_url(str(params.get("url", "")))
            if action == "search_web":
                return self.browser.search_web(str(params.get("query", "")))

        if tool == "code" and action == "run":
            return self.code.run(str(params.get("command", "")), int(params.get("timeout_sec", 30)))

        if tool == "email":
            if action == "queue":
                return self.email.queue_email(
                    to=str(params.get("to", "")),
                    subject=str(params.get("subject", "")),
                    body=str(params.get("body", "")),
                )
            if action == "list":
                return self.email.list_queue()

        if tool == "scheduler":
            if action == "create":
                run_at = str(params.get("run_at", "")).strip()
                if not run_at:
                    run_at = datetime.now(UTC).isoformat()
                payload = {
                    "tool": str(params.get("tool", "")),
                    "action": str(params.get("action", "")),
                    "params": dict(params.get("params", {})),
                    "confirm": bool(params.get("confirm", False)),
                }
                created = self.scheduler.add_job(session_id, run_at, payload)
                return {"ok": True, "job": created}
            if action == "list":
                status = params.get("status")
                status_str = str(status) if status else None
                return {"ok": True, "jobs": self.scheduler.list_jobs(status_str)}
            if action == "run_due":
                return self.run_due_jobs()

        return {"ok": False, "message": f"Unsupported tool/action: {tool}/{action}"}
