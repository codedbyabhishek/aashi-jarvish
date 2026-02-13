from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import threading
import time
from typing import Any

from ashi_os.voice.listener import VoiceCommandPipeline


_AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".aac", ".aiff"}


@dataclass
class _RuntimeConfig:
    session_id: str
    speak_reply: bool


class ContinuousVoiceRuntime:
    def __init__(
        self,
        pipeline: VoiceCommandPipeline,
        orchestrator,
        inbox_dir: Path,
        processed_dir: Path,
        poll_interval_sec: float,
    ) -> None:
        self.pipeline = pipeline
        self.orchestrator = orchestrator
        self.inbox_dir = inbox_dir
        self.processed_dir = processed_dir
        self.poll_interval_sec = max(0.2, poll_interval_sec)

        self._thread: threading.Thread | None = None
        self._running = False
        self._lock = threading.Lock()
        self._cfg = _RuntimeConfig(session_id="default", speak_reply=True)
        self._last_error = ""
        self._events: list[dict[str, Any]] = []

        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def start(self, session_id: str, speak_reply: bool) -> dict:
        with self._lock:
            self._cfg = _RuntimeConfig(session_id=session_id, speak_reply=speak_reply)
            if self._running:
                pass
            else:
                self._running = True
                self._last_error = ""
                self._thread = threading.Thread(target=self._loop, daemon=True)
                self._thread.start()
        return self.status()

    def stop(self) -> dict:
        with self._lock:
            self._running = False
            thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=1.5)
        return self.status()

    def status(self) -> dict:
        with self._lock:
            running = self._running
            cfg = self._cfg
            last_error = self._last_error
            events = list(self._events[-10:])

        return {
            "running": running,
            "session_id": cfg.session_id,
            "speak_reply": cfg.speak_reply,
            "wake_phrase": self.pipeline.wake_phrase,
            "inbox_dir": str(self.inbox_dir),
            "processed_dir": str(self.processed_dir),
            "last_error": last_error,
            "recent_events": events,
        }

    def _loop(self) -> None:
        while True:
            with self._lock:
                if not self._running:
                    return
                cfg = self._cfg

            try:
                files = sorted(
                    [p for p in self.inbox_dir.iterdir() if p.is_file() and p.suffix.lower() in _AUDIO_EXTS],
                    key=lambda p: p.stat().st_mtime,
                )
            except Exception as exc:
                self._set_error(f"Failed reading voice inbox: {exc}")
                time.sleep(self.poll_interval_sec)
                continue

            for file_path in files:
                try:
                    result = self.pipeline.run_file(
                        session_id=cfg.session_id,
                        file_path=file_path,
                        orchestrator=self.orchestrator,
                        speak_reply=cfg.speak_reply,
                    )
                    self._append_event(
                        {
                            "file": file_path.name,
                            "ok": result.get("ok", False),
                            "command": result.get("command", ""),
                            "reply": result.get("reply", ""),
                        }
                    )
                    target = self.processed_dir / f"{int(time.time())}_{file_path.name}"
                    shutil.move(str(file_path), str(target))
                except Exception as exc:
                    self._set_error(f"Voice loop failed for {file_path.name}: {exc}")

            time.sleep(self.poll_interval_sec)

    def _set_error(self, message: str) -> None:
        with self._lock:
            self._last_error = message
            self._append_event({"ok": False, "error": message})

    def _append_event(self, event: dict[str, Any]) -> None:
        self._events.append({"ts": int(time.time()), **event})
        if len(self._events) > 50:
            self._events = self._events[-50:]
