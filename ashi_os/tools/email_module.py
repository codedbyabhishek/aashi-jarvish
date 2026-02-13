from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
import json


@dataclass
class EmailRecord:
    created_at: str
    to: str
    subject: str
    body: str


class EmailModule:
    def __init__(self, queue_file: Path) -> None:
        self.queue_file = queue_file
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)

    def queue_email(self, to: str, subject: str, body: str) -> dict:
        if "@" not in to:
            return {"ok": False, "message": "Invalid recipient email."}

        record = EmailRecord(
            created_at=datetime.now(UTC).isoformat(),
            to=to.strip(),
            subject=subject.strip(),
            body=body,
        )
        items = self._load()
        items.append(record.__dict__)
        self.queue_file.write_text(json.dumps(items, indent=2), encoding="utf-8")
        return {"ok": True, "message": "Email queued (dry-run).", "queued_count": len(items)}

    def list_queue(self) -> dict:
        items = self._load()
        return {"ok": True, "items": items}

    def _load(self) -> list[dict]:
        if not self.queue_file.exists():
            return []
        try:
            data = json.loads(self.queue_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        if not isinstance(data, list):
            return []
        return data
