import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashi_os.core.security import redact_secrets


class AuditLogger:
    def __init__(self, log_dir: Path) -> None:
        self.path = log_dir / "audit.jsonl"

    def write(self, event: str, payload: dict[str, Any]) -> None:
        item = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "payload": {k: redact_secrets(str(v)) for k, v in payload.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(item, ensure_ascii=True) + "\n")
