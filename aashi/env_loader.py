from pathlib import Path
import os


def load_local_env_files() -> None:
    for name in (".env", ".env.local"):
        _load_env_file(Path(name))


def _load_env_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        return

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue

        os.environ.setdefault(key, value)
