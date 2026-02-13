from pathlib import Path
import shlex
import subprocess


class CodeRunnerModule:
    ALLOWED_PREFIXES = {
        "python",
        "python3",
        "pytest",
        "uvicorn",
        "pip",
        "rg",
        "ls",
        "pwd",
        "echo",
    }

    BLOCKED_TOKENS = {"rm", "shutdown", "reboot", "mkfs", "dd", "sudo"}

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root

    def run(self, command: str, timeout_sec: int = 30) -> dict:
        command = command.strip()
        if not command:
            return {"ok": False, "message": "command is required."}

        parts = shlex.split(command)
        if not parts:
            return {"ok": False, "message": "Invalid command."}

        if any(token in self.BLOCKED_TOKENS for token in parts):
            return {"ok": False, "message": "Command blocked by safety policy."}

        if parts[0] not in self.ALLOWED_PREFIXES:
            return {
                "ok": False,
                "message": f"Command prefix '{parts[0]}' is not allowed.",
                "allowed": sorted(self.ALLOWED_PREFIXES),
            }

        try:
            result = subprocess.run(
                parts,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "message": "Command timed out."}

        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[-12000:],
            "stderr": result.stderr[-12000:],
        }
