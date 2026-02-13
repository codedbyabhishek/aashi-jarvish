from datetime import datetime, UTC
from pathlib import Path
import json
import sqlite3


class SchedulerStore:
    def __init__(self, sqlite_path: Path) -> None:
        self.sqlite_path = sqlite_path
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_table()

    def _connect(self):
        return sqlite3.connect(str(self.sqlite_path))

    def _init_table(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scheduler_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    run_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add_job(self, session_id: str, run_at: str, payload: dict) -> dict:
        now = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO scheduler_jobs (session_id, run_at, payload_json, status, created_at, updated_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
                """,
                (session_id, run_at, json.dumps(payload), now, now),
            )
            conn.commit()
            return {"id": cur.lastrowid, "status": "pending"}

    def list_jobs(self, status: str | None = None) -> list[dict]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    "SELECT id, session_id, run_at, payload_json, status, created_at, updated_at FROM scheduler_jobs WHERE status=? ORDER BY id DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, session_id, run_at, payload_json, status, created_at, updated_at FROM scheduler_jobs ORDER BY id DESC"
                ).fetchall()

        out = []
        for row in rows:
            out.append(
                {
                    "id": row[0],
                    "session_id": row[1],
                    "run_at": row[2],
                    "payload": json.loads(row[3]),
                    "status": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                }
            )
        return out

    def due_jobs(self) -> list[dict]:
        now = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, run_at, payload_json, status, created_at, updated_at
                FROM scheduler_jobs
                WHERE status='pending' AND run_at <= ?
                ORDER BY run_at ASC, id ASC
                """,
                (now,),
            ).fetchall()

        return [
            {
                "id": row[0],
                "session_id": row[1],
                "run_at": row[2],
                "payload": json.loads(row[3]),
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }
            for row in rows
        ]

    def mark_job(self, job_id: int, status: str) -> None:
        now = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            conn.execute(
                "UPDATE scheduler_jobs SET status=?, updated_at=? WHERE id=?",
                (status, now, job_id),
            )
            conn.commit()
