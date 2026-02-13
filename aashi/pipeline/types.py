from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class InputPacket:
    raw_text: str
    text: str


@dataclass(frozen=True)
class Intent:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Plan:
    actions: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ExecutionResult:
    ok: bool
    message: str
