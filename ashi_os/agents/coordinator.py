from ashi_os.agents.execution_agent import ExecutionAgent
from ashi_os.agents.memory_agent import MemoryAgent
from ashi_os.agents.research_agent import ResearchAgent
from ashi_os.agents.supervisor_agent import SupervisorAgent
from ashi_os.agents.validation_agent import ValidationAgent
from ashi_os.brain.confirmation import ConfirmationManager
from ashi_os.brain.planning import RiskEvaluator, StrategicPlanner
from ashi_os.logging.audit_log import AuditLogger


class AgentCoordinator:
    def __init__(
        self,
        research: ResearchAgent,
        execution: ExecutionAgent,
        validation: ValidationAgent,
        memory_agent: MemoryAgent,
        supervisor: SupervisorAgent,
        planner: StrategicPlanner,
        risk_evaluator: RiskEvaluator,
        confirmation: ConfirmationManager,
        audit: AuditLogger,
    ) -> None:
        self.research = research
        self.execution = execution
        self.validation = validation
        self.memory_agent = memory_agent
        self.supervisor = supervisor
        self.planner = planner
        self.risk_evaluator = risk_evaluator
        self.confirmation = confirmation
        self.audit = audit

    def run(
        self,
        session_id: str,
        objective: str,
        auto_execute: bool,
        confirm_token: str | None = None,
    ) -> dict:
        confirmed = False
        restored_objective = ""
        if confirm_token:
            confirmed, restored_objective = self.confirmation.consume_token(session_id, confirm_token)
            if confirmed:
                objective = restored_objective

        plan = self.planner.build_plan(objective)
        risk = self.risk_evaluator.evaluate(objective, plan)

        if risk.confirmation_required and not confirmed:
            existing_token = self.confirmation.pending_token(session_id)
            token = existing_token or self.confirmation.create(session_id, objective)
            summary = self.supervisor.summarize(
                objective=objective,
                plan=plan.as_dict(),
                risk=risk.as_dict(),
                validation={"summary": "Awaiting confirmation."},
                confirmation_required=True,
            )
            self.audit.write(
                "agents.confirmation_required",
                {
                    "session_id": session_id,
                    "objective": objective,
                    "risk_level": risk.level,
                    "token": token,
                },
            )
            return {
                "ok": True,
                "objective": objective,
                "plan": plan.as_dict(),
                "risk": risk.as_dict(),
                "research": {},
                "proposed_actions": [],
                "execution_results": [],
                "validation": {"ok": False, "summary": "Confirmation required before execution."},
                "supervisor_summary": summary,
                "confirmation_required": True,
                "confirmation_token": token,
            }

        research_out = self.research.run(session_id=session_id, objective=objective)
        proposed_actions = self.execution.propose_actions(plan.as_dict().get("steps", []))

        execution_results = []
        if auto_execute and proposed_actions:
            execution_results = self.execution.execute(
                session_id=session_id,
                actions=proposed_actions,
                confirm=confirmed,
            )

        validation_out = self.validation.run(execution_results=execution_results, auto_execute=auto_execute)
        memory_out = self.memory_agent.store_reflection(
            session_id=session_id,
            objective=objective,
            validation=validation_out,
        )

        summary = self.supervisor.summarize(
            objective=objective,
            plan=plan.as_dict(),
            risk=risk.as_dict(),
            validation=validation_out,
            confirmation_required=False,
        )

        self.audit.write(
            "agents.completed",
            {
                "session_id": session_id,
                "objective": objective,
                "risk_level": risk.level,
                "auto_execute": auto_execute,
                "actions": len(proposed_actions),
                "success": validation_out.get("success_count", 0),
                "failure": validation_out.get("failure_count", 0),
            },
        )

        return {
            "ok": True,
            "objective": objective,
            "plan": plan.as_dict(),
            "risk": risk.as_dict(),
            "research": research_out,
            "proposed_actions": proposed_actions,
            "execution_results": execution_results,
            "validation": validation_out,
            "memory": memory_out,
            "supervisor_summary": summary,
            "confirmation_required": False,
            "confirmation_token": None,
        }

    def status(self) -> dict:
        return {
            "agents": ["research", "execution", "validation", "memory", "supervisor"],
            "confirmation_model": "token_challenge",
        }
