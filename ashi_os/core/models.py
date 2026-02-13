from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    user_message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    provider: str
    model: str
    plan: dict = Field(default_factory=dict)
    risk: dict = Field(default_factory=dict)
    confirmation_required: bool = False
    confirmation_token: str | None = None


class MemoryAddRequest(BaseModel):
    session_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    metadata: dict = Field(default_factory=dict)


class MemorySearchRequest(BaseModel):
    session_id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    top_k: int = 5


class VoiceCommandFileRequest(BaseModel):
    session_id: str = Field(min_length=1)
    file_path: str = Field(min_length=1)
    speak_reply: bool = True


class VoiceStartRequest(BaseModel):
    session_id: str = Field(min_length=1)
    speak_reply: bool = True


class ToolExecuteRequest(BaseModel):
    session_id: str = Field(min_length=1)
    tool: str = Field(min_length=1)
    action: str = Field(min_length=1)
    params: dict = Field(default_factory=dict)
    confirm: bool = False


class SchedulerCreateRequest(BaseModel):
    session_id: str = Field(min_length=1)
    run_at: str = Field(min_length=1)
    tool: str = Field(min_length=1)
    action: str = Field(min_length=1)
    params: dict = Field(default_factory=dict)
    confirm: bool = False


class AgentRunRequest(BaseModel):
    session_id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    auto_execute: bool = False
    confirm_token: str | None = None


class AgentRunResponse(BaseModel):
    ok: bool = True
    objective: str
    plan: dict = Field(default_factory=dict)
    risk: dict = Field(default_factory=dict)
    research: dict = Field(default_factory=dict)
    proposed_actions: list[dict] = Field(default_factory=list)
    execution_results: list[dict] = Field(default_factory=list)
    validation: dict = Field(default_factory=dict)
    memory: dict = Field(default_factory=dict)
    supervisor_summary: str = ""
    confirmation_required: bool = False
    confirmation_token: str | None = None
