"""
Agent service: orchestrates RAG retrieval + LLM generation for customer service chat.
Saves conversation history to PostgreSQL on every turn.
"""
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.config.settings import settings
from app.models.agent import AgentRun, AgentStep
from app.models.conversation import Conversation, ConversationMessage
from app.rag.retriever import Retriever
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.logger import logger

# System prompt template: RAG context is injected into {context} at runtime
RAG_SYSTEM_PROMPT = """你是一个专业的数码商城AI客服助手。

## 核心规则
1. **基于参考资料回答**：所有商品数据和政策信息必须来自下方提供的参考知识库。如果没有找到相关信息，诚实告知用户你不知道。
2. **引用来源**：回答时注明信息来源。
3. **禁止编造**：绝对不要猜测或编造不存在的信息。
4. **如实回答**：如果不知道答案，明确告知用户，并建议联系人工客服。

## 参考知识库
{context}"""


class AgentService:
    """Chat service with RAG-powered answering."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._retriever: Retriever | None = None
        self._llm = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self._model = settings.llm_model

    async def chat(self, user_id: int, request: ChatRequest) -> ChatResponse:
        """Handle a chat message: retrieve context, call LLM, persist conversation."""
        start = perf_counter()

        # 1. Resolve or create a conversation before writing any user data.
        conv_id = request.conversation_id
        if conv_id is None:
            conv = Conversation(user_id=user_id, title=request.message[:50])
            self._session.add(conv)
            await self._session.flush()
            conv_id = conv.id
        else:
            conv = await self._session.get(Conversation, conv_id)
            if conv is None:
                raise ValueError("Conversation not found")
            if conv.user_id != user_id:
                raise PermissionError("Conversation does not belong to current user")

        # 2. Create a trace run for the current chat turn.
        run = AgentRun(
            conversation_id=conv_id,
            query=request.message,
            intent="RAG",
            status="RUNNING",
        )
        self._session.add(run)
        await self._session.flush()

        # 3. Retrieve relevant knowledge from Qdrant, with a no-context fallback.
        retrieve_start = perf_counter()
        context = ""
        sources: list[str] = []
        retrieval_error: str | None = None
        try:
            if self._retriever is None:
                self._retriever = Retriever()
            context, sources = await self._retriever.format_context(request.message, top_k=5)
        except Exception as exc:
            logger.exception("RAG retrieval failed")
            retrieval_error = str(exc)

        retrieval_ms = int((perf_counter() - retrieve_start) * 1000)
        self._session.add(
            AgentStep(
                run_id=run.id,
                node_name="rag_retrieval",
                input_data={"query": request.message, "top_k": 5},
                output_data={
                    "sources": sources,
                    "context_found": bool(context),
                    "error": retrieval_error,
                },
                duration_ms=retrieval_ms,
            )
        )

        # 4. Build prompt with context injected.
        system_prompt = RAG_SYSTEM_PROMPT.format(
            context=context if context else "（暂无相关参考文档，请如实告知用户你无法回答此问题）"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message},
        ]

        # 5. Call LLM.
        llm_start = perf_counter()
        llm_error: str | None = None
        try:
            resp = await self._llm.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            answer = resp.choices[0].message.content or ""
        except Exception as exc:
            logger.exception("LLM chat call failed")
            llm_error = str(exc)
            answer = "抱歉，AI服务暂时不可用，请稍后再试或联系人工客服。"

        llm_ms = int((perf_counter() - llm_start) * 1000)
        self._session.add(
            AgentStep(
                run_id=run.id,
                node_name="response_generation",
                input_data={"model": self._model, "has_context": bool(context)},
                output_data={"answer_preview": answer[:200], "error": llm_error},
                duration_ms=llm_ms,
            )
        )

        # 6. Persist conversation and messages.
        user_msg = ConversationMessage(
            conversation_id=conv_id,
            role="user",
            content=request.message,
        )
        self._session.add(user_msg)

        assistant_msg = ConversationMessage(
            conversation_id=conv_id,
            role="assistant",
            content=answer,
            sources=str(sources) if sources else None,
        )
        self._session.add(assistant_msg)

        run.status = "COMPLETED"
        run.latency_ms = int((perf_counter() - start) * 1000)
        await self._session.flush()

        return ChatResponse(
            conversation_id=conv_id,
            answer=answer,
            intent="RAG",
            sources=sources,
        )
