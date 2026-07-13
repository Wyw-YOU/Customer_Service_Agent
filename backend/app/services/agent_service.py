from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat import ChatRequest, ChatResponse


class AgentService:
    """Agent chat service skeleton. Full LangGraph implementation in Phase 3."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def chat(self, user_id: int, request: ChatRequest) -> ChatResponse:
        """Placeholder: echoes the message. Will be replaced with LangGraph agent."""
        return ChatResponse(
            conversation_id=request.conversation_id or 1,
            answer=f"[MVP Placeholder] Received: {request.message}. Agent coming in Phase 3.",
            intent="GENERAL",
            sources=[],
        )
