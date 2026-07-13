from typing import Any, TypedDict


class AgentState(TypedDict):
    user_id: int
    query: str
    messages: list
    intent: str
    confidence: float
    task_type: str
    analysis: dict[str, Any]
    retrieved_docs: list
    rag_context: str
    sources: list[str]
    tool_results: dict
    memory: dict
    risk_level: str
    need_human: bool
    response: str
    errors: list[dict[str, Any]]
    trace_steps: list[dict[str, Any]]


def create_initial_state(user_id: int, query: str, messages: list = None) -> AgentState:
    return AgentState(
        user_id=user_id,
        query=query,
        messages=messages or [],
        intent="",
        confidence=0.0,
        task_type="",
        analysis={},
        retrieved_docs=[],
        rag_context="",
        sources=[],
        tool_results={},
        memory={},
        risk_level="LOW",
        need_human=False,
        response="",
        errors=[],
        trace_steps=[],
    )
