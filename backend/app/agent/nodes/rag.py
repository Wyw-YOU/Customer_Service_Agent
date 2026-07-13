"""RAG retrieval node."""

from time import perf_counter

from app.agent.nodes.common import add_step, elapsed_ms
from app.agent.runtime import AgentRuntime
from app.agent.state import AgentState
from app.rag.retriever import Retriever
from app.utils.logger import logger


def create_rag_node(runtime: AgentRuntime):
    async def rag_node(state: AgentState) -> AgentState:
        start = perf_counter()
        error: str | None = None
        context = ""
        sources: list[str] = []
        try:
            context, sources = await Retriever().format_context(state["query"], top_k=5)
        except Exception as exc:
            logger.exception("RAG retrieval failed in agent workflow")
            error = str(exc)
            state["errors"].append({"node": "rag_retrieval", "error": error})

        state["rag_context"] = context
        state["sources"] = sources
        state["retrieved_docs"] = [{"source": source} for source in sources]
        add_step(
            state,
            "rag_retrieval",
            {"query": state["query"], "top_k": 5},
            {"sources": sources, "context_found": bool(context), "error": error},
            elapsed_ms(start),
        )
        return state

    return rag_node
