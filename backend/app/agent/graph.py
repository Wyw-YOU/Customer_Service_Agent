"""LangGraph assembly for the customer service agent."""

from langgraph.graph import END, StateGraph

from app.agent.nodes.analyzer import query_analyzer
from app.agent.nodes.human import human_node
from app.agent.nodes.rag import create_rag_node
from app.agent.nodes.response import create_response_generator
from app.agent.nodes.router import intent_router, route_after_analysis
from app.agent.nodes.tool import (
    create_order_tool_node,
    create_product_tool_node,
    create_refund_tool_node,
)
from app.agent.runtime import AgentRuntime
from app.agent.state import AgentState


def build_agent_graph(runtime: AgentRuntime | None = None):
    runtime = runtime or AgentRuntime()

    graph = StateGraph(AgentState)
    graph.add_node("intent_router", intent_router)
    graph.add_node("query_analyzer", query_analyzer)
    graph.add_node("rag", create_rag_node(runtime))
    graph.add_node("product", create_product_tool_node(runtime))
    graph.add_node("order", create_order_tool_node(runtime))
    graph.add_node("refund", create_refund_tool_node(runtime))
    graph.add_node("human", human_node)
    graph.add_node("response", create_response_generator(runtime))

    graph.set_entry_point("intent_router")
    graph.add_edge("intent_router", "query_analyzer")
    graph.add_conditional_edges(
        "query_analyzer",
        route_after_analysis,
        {
            "rag": "rag",
            "product": "product",
            "order": "order",
            "refund": "refund",
            "human": "human",
        },
    )
    graph.add_edge("rag", "response")
    graph.add_edge("product", "rag")
    graph.add_edge("order", "response")
    graph.add_edge("refund", "response")
    graph.add_edge("human", "response")
    graph.add_edge("response", END)
    return graph.compile()


async def run_agent(
    state: AgentState,
    runtime: AgentRuntime | None = None,
) -> AgentState:
    """Run the MVP LangGraph workflow."""
    graph = build_agent_graph(runtime)
    return await graph.ainvoke(state)
