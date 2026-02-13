from fastapi import APIRouter, Request

from ashi_os.core.models import SchedulerCreateRequest, ToolExecuteRequest

router = APIRouter(tags=["tools"])


@router.get("/tools/catalog")
def tools_catalog(request: Request) -> dict:
    executor = request.app.state.tool_executor
    return {"tools": executor.catalog()}


@router.post("/tools/execute")
def tools_execute(payload: ToolExecuteRequest, request: Request) -> dict:
    executor = request.app.state.tool_executor
    result = executor.execute(
        session_id=payload.session_id,
        tool=payload.tool,
        action=payload.action,
        params=payload.params,
        confirm=payload.confirm,
    )
    return result


@router.post("/scheduler/jobs")
def scheduler_create(payload: SchedulerCreateRequest, request: Request) -> dict:
    executor = request.app.state.tool_executor
    result = executor.execute(
        session_id=payload.session_id,
        tool="scheduler",
        action="create",
        params={
            "run_at": payload.run_at,
            "tool": payload.tool,
            "action": payload.action,
            "params": payload.params,
            "confirm": payload.confirm,
        },
        confirm=True,
    )
    return result


@router.get("/scheduler/jobs")
def scheduler_list(request: Request, status: str | None = None) -> dict:
    executor = request.app.state.tool_executor
    return executor.execute(
        session_id="scheduler",
        tool="scheduler",
        action="list",
        params={"status": status} if status else {},
        confirm=True,
    )


@router.post("/scheduler/run-due")
def scheduler_run_due(request: Request) -> dict:
    executor = request.app.state.tool_executor
    return executor.execute(
        session_id="scheduler",
        tool="scheduler",
        action="run_due",
        params={},
        confirm=True,
    )
