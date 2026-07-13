"""Agent service: persists chat turns and delegates execution to LangGraph."""

from time import perf_counter

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.graph import run_agent
from app.agent.runtime import AgentRuntime
from app.agent.state import create_initial_state
from app.models.agent import AgentRun, AgentStep
from app.models.conversation import Conversation, ConversationMessage
from app.schemas.chat import ChatRequest, ChatResponse


class AgentService:
    """Chat service backed by the MVP LangGraph workflow."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def chat(self, user_id: int, request: ChatRequest) -> ChatResponse:
        """Handle a chat message, save conversation history, and write agent trace."""
        start = perf_counter()
        conv_id = await self._resolve_conversation(user_id, request)

        run = AgentRun(
            conversation_id=conv_id,
            query=request.message,
            intent="UNKNOWN",
            status="RUNNING",
        )
        self._session.add(run)
        await self._session.flush()

        state = create_initial_state(user_id=user_id, query=request.message)
        runtime = AgentRuntime(db_session=self._session)
        state = await run_agent(state, runtime=runtime)

        for step in state["trace_steps"]:
            self._session.add(
                AgentStep(
                    run_id=run.id,
                    node_name=step["node_name"],
                    input_data=step.get("input_data"),
                    output_data=step.get("output_data"),
                    duration_ms=step.get("duration_ms"),
                )
            )

        answer = state["response"]
        self._session.add(
            ConversationMessage(
                conversation_id=conv_id,
                role="user",
                content=request.message,
            )
        )
        self._session.add(
            ConversationMessage(
                conversation_id=conv_id,
                role="assistant",
                content=answer,
                sources=str(state["sources"]) if state["sources"] else None,
            )
        )

        run.intent = state["intent"]
        run.confidence = state["confidence"]
        run.status = "COMPLETED" if not state["errors"] else "COMPLETED_WITH_WARNINGS"
        run.latency_ms = int((perf_counter() - start) * 1000)
        await self._session.flush()

        return ChatResponse(
            conversation_id=conv_id,
            answer=answer,
            intent=state["intent"],
            sources=state["sources"],
        )

    async def _resolve_conversation(self, user_id: int, request: ChatRequest) -> int:
        if request.conversation_id is None:
            conversation = Conversation(user_id=user_id, title=request.message[:50])
            self._session.add(conversation)
            await self._session.flush()
            return conversation.id

        conversation = await self._session.get(Conversation, request.conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found")
        if conversation.user_id != user_id:
            raise PermissionError("Conversation does not belong to current user")
        return conversation.id
