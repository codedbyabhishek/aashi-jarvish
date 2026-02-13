
class SupervisorAgent:
    def summarize(self, objective: str, plan: dict, risk: dict, validation: dict, confirmation_required: bool) -> str:
        if confirmation_required:
            return (
                f"Objective '{objective}' is high risk. "
                "Execution paused until confirmation token is provided."
            )

        step_count = len(plan.get("steps", []))
        risk_level = risk.get("level", "unknown")
        return (
            f"Objective analyzed. Plan has {step_count} steps. "
            f"Risk level: {risk_level}. {validation.get('summary', '')}"
        )
