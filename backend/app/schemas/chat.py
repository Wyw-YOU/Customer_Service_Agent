from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    intent: str | None = None
    sources: list[str] | None = None
