from fastapi import APIRouter, Request

from ashi_os.core.models import ChatRequest, ChatResponse, MemoryAddRequest, MemorySearchRequest

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    orchestrator = request.app.state.orchestrator
    reply, provider, model = orchestrator.chat(session_id=payload.session_id, user_message=payload.user_message)
    return ChatResponse(session_id=payload.session_id, reply=reply, provider=provider, model=model)


@router.post("/memory/add")
def memory_add(payload: MemoryAddRequest, request: Request) -> dict:
    memory = request.app.state.memory
    memory_id = memory.add_memory(payload.session_id, payload.text, payload.metadata)
    return {"id": memory_id}


@router.post("/memory/search")
def memory_search(payload: MemorySearchRequest, request: Request) -> dict:
    memory = request.app.state.memory
    hits = memory.search(payload.session_id, payload.query, payload.top_k)
    return {"hits": hits}
