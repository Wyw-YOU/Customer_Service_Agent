"""Intent routing node and graph routing rules."""

from time import perf_counter

from app.agent.nodes.common import add_step, elapsed_ms
from app.agent.state import AgentState


async def intent_router(state: AgentState) -> AgentState:
    start = perf_counter()
    query = state["query"].lower()

    intent = "OTHER"
    confidence = 0.6
    if any(word in query for word in ("退款", "退货", "换货", "售后")):
        intent = "AFTERSALE_REQUEST"
        confidence = 0.9
    elif any(word in query for word in ("订单", "物流", "快递", "到哪", "发货")):
        logistics_words = ("物流", "快递", "到哪", "发货")
        has_logistics_word = any(word in query for word in logistics_words)
        intent = "LOGISTICS_QUERY" if has_logistics_word else "ORDER_QUERY"
        confidence = 0.85
    elif any(word in query for word in ("推荐", "预算", "以内", "适合", "买什么")):
        intent = "PRODUCT_RECOMMEND"
        confidence = 0.85
    elif any(word in query for word in ("商品", "手机", "电脑", "耳机", "平板", "价格", "参数")):
        intent = "PRODUCT_QUERY"
        confidence = 0.75
    elif any(word in query for word in ("投诉", "人工", "客服")):
        intent = "COMPLAINT"
        confidence = 0.9

    state["intent"] = intent
    state["confidence"] = confidence
    add_step(
        state,
        "intent_router",
        {"query": state["query"]},
        {"intent": intent, "confidence": confidence},
        elapsed_ms(start),
    )
    return state


def route_after_analysis(state: AgentState) -> str:
    if state["confidence"] < 0.55 or state["intent"] == "COMPLAINT":
        return "human"
    if state["intent"] in {"PRODUCT_QUERY", "PRODUCT_RECOMMEND", "PRODUCT_COMPARE"}:
        return "product"
    if state["intent"] in {"ORDER_QUERY", "LOGISTICS_QUERY"}:
        return "order"
    if state["intent"] == "AFTERSALE_REQUEST":
        return "refund"
    return "rag"
