from dataclasses import dataclass
import re


@dataclass
class PlanStep:
    id: int
    task: str
    rationale: str


@dataclass
class ExecutionPlan:
    objective: str
    steps: list[PlanStep]

    def as_dict(self) -> dict:
        return {
            "objective": self.objective,
            "steps": [
                {
                    "id": step.id,
                    "task": step.task,
                    "rationale": step.rationale,
                }
                for step in self.steps
            ],
        }


@dataclass
class RiskAssessment:
    level: str
    score: int
    reasons: list[str]
    confirmation_required: bool

    def as_dict(self) -> dict:
        return {
            "level": self.level,
            "score": self.score,
            "reasons": self.reasons,
            "confirmation_required": self.confirmation_required,
        }


class StrategicPlanner:
    def build_plan(self, user_message: str) -> ExecutionPlan:
        objective = user_message.strip() or "Handle request"
        parts = self._split_steps(objective)
        steps: list[PlanStep] = []

        for idx, part in enumerate(parts, start=1):
            task = part.strip().strip(".")
            if not task:
                continue
            rationale = "Required to progress toward the objective."
            if idx == 1:
                rationale = "Establish initial execution direction."
            elif idx == len(parts):
                rationale = "Finalize and validate outcome."
            steps.append(PlanStep(id=idx, task=task, rationale=rationale))

        if not steps:
            steps = [PlanStep(id=1, task="Clarify intent", rationale="No clear task segments detected.")]

        return ExecutionPlan(objective=objective, steps=steps)

    def _split_steps(self, text: str) -> list[str]:
        chunks = re.split(r"\b(?:then|and then|after that|next|finally|and)\b", text, flags=re.IGNORECASE)
        cleaned = [chunk.strip(" ,") for chunk in chunks if chunk.strip(" ,")]
        if len(cleaned) <= 1 and "," in text:
            cleaned = [x.strip() for x in text.split(",") if x.strip()]
        return cleaned[:8]


class RiskEvaluator:
    HIGH_RISK_TERMS = {
        "delete",
        "rm -rf",
        "shutdown",
        "reboot",
        "drop table",
        "format disk",
        "erase",
        "credentials",
        "password",
        "api key",
        "bank",
        "transfer",
        "payment",
    }
    MEDIUM_RISK_TERMS = {
        "install",
        "sudo",
        "email",
        "send mail",
        "automation",
        "schedule",
        "run command",
        "execute",
        "open site",
        "signup",
        "create key",
    }

    def evaluate(self, user_message: str, plan: ExecutionPlan) -> RiskAssessment:
        lower = user_message.lower()
        score = 0
        reasons: list[str] = []
        high_hit = False

        for token in sorted(self.HIGH_RISK_TERMS):
            if token in lower:
                score += 3
                reasons.append(f"High-risk indicator: '{token}'")
                high_hit = True

        for token in sorted(self.MEDIUM_RISK_TERMS):
            if token in lower:
                score += 1
                reasons.append(f"Medium-risk indicator: '{token}'")

        if len(plan.steps) >= 4:
            score += 1
            reasons.append("Multi-step request complexity")

        if high_hit or score >= 4:
            level = "high"
        elif score >= 2:
            level = "medium"
        else:
            level = "low"

        confirmation_required = level == "high"
        if confirmation_required and "Explicit user confirmation required" not in reasons:
            reasons.append("Explicit user confirmation required")

        return RiskAssessment(level=level, score=score, reasons=reasons, confirmation_required=confirmation_required)
