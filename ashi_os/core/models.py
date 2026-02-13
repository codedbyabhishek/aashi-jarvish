from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    user_message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    provider: str
    model: str


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
