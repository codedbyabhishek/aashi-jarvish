from fastapi import APIRouter, Request

from ashi_os.core.models import AgentRunRequest, AgentRunResponse

router = APIRouter(tags=["agents"])


@router.get("/agents/status")
def agents_status(request: Request) -> dict:
    coordinator = request.app.state.agent_coordinator
    return coordinator.status()


@router.post("/agents/run", response_model=AgentRunResponse)
def agents_run(payload: AgentRunRequest, request: Request) -> AgentRunResponse:
    coordinator = request.app.state.agent_coordinator
    result = coordinator.run(
        session_id=payload.session_id,
        objective=payload.objective,
        auto_execute=payload.auto_execute,
        confirm_token=payload.confirm_token,
    )
    return AgentRunResponse(**result)
