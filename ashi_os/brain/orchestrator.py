from ashi_os.brain.confirmation import ConfirmationManager
from ashi_os.brain.context_manager import ContextManager
from ashi_os.brain.llm_router import LLMRouter
from ashi_os.brain.planning import RiskEvaluator, StrategicPlanner
from ashi_os.core.security import is_destructive_command
from ashi_os.logging.audit_log import AuditLogger
from ashi_os.memory.memory_service import MemoryService


class Orchestrator:
    def __init__(
        self,
        router: LLMRouter,
        context_manager: ContextManager,
        memory: MemoryService,
        audit: AuditLogger,
        memory_on_chat: bool,
    ) -> None:
        self.router = router
        self.context_manager = context_manager
        self.memory = memory
        self.audit = audit
        self.memory_on_chat = memory_on_chat
        self._sessions: dict[str, list[dict[str, str]]] = {}

        self.planner = StrategicPlanner()
        self.risk = RiskEvaluator()
        self.confirmation = ConfirmationManager()

    def chat(self, session_id: str, user_message: str) -> dict:
        confirmed, restored_message = self.confirmation.consume_if_valid(session_id, user_message)
        if confirmed and not restored_message:
            return {
                "reply": "Invalid confirmation token. Use the exact token previously provided.",
                "provider": "policy",
                "model": "confirm_gate",
                "plan": {},
                "risk": {"level": "high", "confirmation_required": True},
                "confirmation_required": True,
                "confirmation_token": None,
            }
        if confirmed and restored_message:
            user_message = restored_message

        if is_destructive_command(user_message):
            token = self.confirmation.create(session_id=session_id, original_message=user_message)
            confirmation = (
                "Risk level elevated. Confirmation required before destructive operations. "
                f"Reply with: confirm {token}"
            )
            self.audit.write("blocked.destructive", {"session_id": session_id, "message": user_message, "token": token})
            return {
                "reply": confirmation,
                "provider": "policy",
                "model": "confirm_gate",
                "plan": {},
                "risk": {
                    "level": "high",
                    "score": 10,
                    "reasons": ["Destructive command pattern detected"],
                    "confirmation_required": True,
                },
                "confirmation_required": True,
                "confirmation_token": token,
            }

        plan = self.planner.build_plan(user_message)
        risk = self.risk.evaluate(user_message, plan)

        if risk.confirmation_required and not confirmed:
            token = self.confirmation.create(session_id=session_id, original_message=user_message)
            reply = (
                f"Risk level {risk.level}. Confirmation required. "
                f"Reply with: confirm {token}"
            )
            self.audit.write(
                "chat.confirmation_required",
                {
                    "session_id": session_id,
                    "user_message": user_message,
                    "token": token,
                    "risk_level": risk.level,
                },
            )
            return {
                "reply": reply,
                "provider": "policy",
                "model": "confirm_gate",
                "plan": plan.as_dict(),
                "risk": risk.as_dict(),
                "confirmation_required": True,
                "confirmation_token": token,
            }

        history = self._sessions.setdefault(session_id, [])
        prompt = self.context_manager.build(
            session_id,
            (
                f"[OBJECTIVE]\n{plan.objective}\n"
                f"[PLAN_STEPS]\n"
                + "\n".join([f"{step.id}. {step.task}" for step in plan.steps])
                + "\n[RISK]\n"
                + f"level={risk.level}; score={risk.score}; reasons={'; '.join(risk.reasons) if risk.reasons else 'none'}\n"
                + "[REQUEST]\n"
                + user_message
            ),
            history,
        )
        reply, provider, model = self.router.generate(prompt)

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})

        if self.memory_on_chat and len(user_message.strip()) > 8:
            self.memory.add_memory(session_id, user_message, {"kind": "user_fact"})

        self.audit.write(
            "chat.completed",
            {
                "session_id": session_id,
                "provider": provider,
                "model": model,
                "user_message": user_message,
                "reply": reply,
                "risk_level": risk.level,
                "plan_steps": len(plan.steps),
            },
        )

        return {
            "reply": reply,
            "provider": provider,
            "model": model,
            "plan": plan.as_dict(),
            "risk": risk.as_dict(),
            "confirmation_required": False,
            "confirmation_token": None,
        }

    def session_history(self, session_id: str) -> list[dict[str, str]]:
        return list(self._sessions.get(session_id, []))
