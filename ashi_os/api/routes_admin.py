from fastapi import APIRouter, Request

router = APIRouter(tags=["admin"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/status/providers")
def provider_status(request: Request) -> dict:
    settings = request.app.state.settings
    return {
        "default_llm": settings.default_llm,
        "fallback_llm": settings.fallback_llm,
        "openai_key_present": bool(settings.openai_api_key),
        "ollama_model": settings.ollama_model,
        "openai_model": settings.openai_model,
    }
