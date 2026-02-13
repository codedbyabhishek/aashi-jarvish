from fastapi import FastAPI

from ashi_os.api.routes_admin import router as admin_router
from ashi_os.api.routes_chat import router as chat_router
from ashi_os.api.routes_voice import router as voice_router
from ashi_os.brain.context_manager import ContextManager
from ashi_os.brain.llm_router import LLMRouter
from ashi_os.brain.orchestrator import Orchestrator
from ashi_os.core.config import get_settings
from ashi_os.logging.audit_log import AuditLogger
from ashi_os.logging.logger import configure_logging
from ashi_os.memory.memory_service import MemoryService


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    memory = MemoryService(settings)
    audit = AuditLogger(settings.log_dir)
    router = LLMRouter(settings)
    context = ContextManager(settings, memory)
    orchestrator = Orchestrator(
        router=router,
        context_manager=context,
        memory=memory,
        audit=audit,
        memory_on_chat=settings.memory_on_chat,
    )

    app = FastAPI(title="ASHI OS", version="0.1.0")
    app.state.settings = settings
    app.state.memory = memory
    app.state.audit = audit
    app.state.orchestrator = orchestrator

    app.include_router(admin_router)
    app.include_router(chat_router)
    app.include_router(voice_router)
    return app


app = create_app()
