import re


_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{10,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z-_]{10,}"),
]


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def is_destructive_command(text: str) -> bool:
    lower = text.lower()
    checks = ["rm -rf", "shutdown", "reboot", "mkfs", "dd if="]
    return any(token in lower for token in checks)
