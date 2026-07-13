"""Business tool nodes for the agent workflow."""

from time import perf_counter

from app.agent.nodes.common import add_step, elapsed_ms
from app.agent.runtime import AgentRuntime
from app.agent.state import AgentState
from app.tools import (
    create_refund_tool,
    get_order_tool,
    list_user_orders_tool,
    search_products_tool,
    tool_error,
)


def _missing_session_result():
    return tool_error("RUNTIME_ERROR", "Database session is not available")


def create_product_tool_node(runtime: AgentRuntime):
    async def product_tool_node(state: AgentState) -> AgentState:
        start = perf_counter()
        analysis = state["analysis"]
        if runtime.db_session is None:
            result = _missing_session_result()
        else:
            result = await search_products_tool(
                runtime.db_session,
                keyword=analysis.get("keyword"),
                budget=analysis.get("budget"),
                category=analysis.get("category"),
            )

        state["tool_results"]["product_search"] = result
        add_step(
            state,
            "product_search_tool",
            {
                "keyword": analysis.get("keyword"),
                "budget": analysis.get("budget"),
                "category": analysis.get("category"),
            },
            result,
            elapsed_ms(start),
        )
        return state

    return product_tool_node


def create_order_tool_node(runtime: AgentRuntime):
    async def order_tool_node(state: AgentState) -> AgentState:
        start = perf_counter()
        order_id = state["analysis"].get("order_id")
        if runtime.db_session is None:
            result = _missing_session_result()
            tool_name = "order_query" if order_id else "order_list"
        elif order_id:
            result = await get_order_tool(
                runtime.db_session,
                user_id=state["user_id"],
                order_id=order_id,
            )
            tool_name = "order_query"
        else:
            result = await list_user_orders_tool(runtime.db_session, user_id=state["user_id"])
            tool_name = "order_list"

        state["tool_results"][tool_name] = result
        add_step(
            state,
            f"{tool_name}_tool",
            {"user_id": state["user_id"], "order_id": order_id},
            result,
            elapsed_ms(start),
        )
        return state

    return order_tool_node


def create_refund_tool_node(runtime: AgentRuntime):
    async def refund_tool_node(state: AgentState) -> AgentState:
        start = perf_counter()
        order_id = state["analysis"].get("order_id")
        if order_id is None:
            result = tool_error("MISSING_ORDER_ID", "请提供需要退款的订单编号。")
        elif runtime.db_session is None:
            result = _missing_session_result()
        else:
            result = await create_refund_tool(
                runtime.db_session,
                user_id=state["user_id"],
                order_id=order_id,
                reason=state["query"],
            )

        state["tool_results"]["refund_create"] = result
        state["risk_level"] = "HIGH"
        state["need_human"] = True
        add_step(
            state,
            "refund_create_tool",
            {"user_id": state["user_id"], "order_id": order_id},
            result,
            elapsed_ms(start),
        )
        return state

    return refund_tool_node
