from dataclasses import dataclass


@dataclass
class AgentReport:
    agent: str
    ok: bool
    summary: str
    data: dict
