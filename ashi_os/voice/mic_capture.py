from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import threading
import time
import wave


@dataclass
class _MicConfig:
    sample_rate: int
    chunk_seconds: float
    channels: int
    device: int | None


class MicrophoneCaptureRuntime:
    def __init__(
        self,
        inbox_dir: Path,
        sample_rate: int,
        chunk_seconds: float,
        channels: int,
        device: int | None,
    ) -> None:
        self.inbox_dir = inbox_dir
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        self._cfg = _MicConfig(
            sample_rate=max(8000, sample_rate),
            chunk_seconds=max(0.5, chunk_seconds),
            channels=max(1, channels),
            device=device,
        )
        self._running = False
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._last_error = ""
        self._captured = 0

    def start(self) -> dict:
        with self._lock:
            if self._running:
                return self.status()
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
            cfg = self._cfg
            return {
                "running": self._running,
                "sample_rate": cfg.sample_rate,
                "chunk_seconds": cfg.chunk_seconds,
                "channels": cfg.channels,
                "device": cfg.device,
                "captured_files": self._captured,
                "last_error": self._last_error,
                "inbox_dir": str(self.inbox_dir),
            }

    def _loop(self) -> None:
        try:
            import numpy as np
            import sounddevice as sd
        except Exception:
            self._set_error("Mic capture requires: pip install sounddevice numpy")
            with self._lock:
                self._running = False
            return

        while True:
            with self._lock:
                if not self._running:
                    return
                cfg = self._cfg

            frames = int(cfg.sample_rate * cfg.chunk_seconds)

            try:
                recording = sd.rec(
                    frames,
                    samplerate=cfg.sample_rate,
                    channels=cfg.channels,
                    dtype="float32",
                    device=cfg.device,
                )
                sd.wait()

                pcm = np.clip(recording, -1.0, 1.0)
                pcm = (pcm * 32767.0).astype(np.int16)

                ts = int(time.time() * 1000)
                out_file = self.inbox_dir / f"mic_{ts}.wav"
                with wave.open(str(out_file), "wb") as wf:
                    wf.setnchannels(cfg.channels)
                    wf.setsampwidth(2)
                    wf.setframerate(cfg.sample_rate)
                    wf.writeframes(pcm.tobytes())

                with self._lock:
                    self._captured += 1
            except Exception as exc:
                self._set_error(f"Mic capture error: {exc}")
                time.sleep(1.0)

    def _set_error(self, message: str) -> None:
        with self._lock:
            self._last_error = message
