"""Query analysis node for extracting MVP tool parameters."""

import re
from time import perf_counter
from typing import Any

from app.agent.nodes.common import add_step, elapsed_ms
from app.agent.state import AgentState


def _extract_first_int(text: str) -> int | None:
    match = re.search(r"\d+", text)
    return int(match.group(0)) if match else None


def _extract_budget(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:元|块|以内|以下|预算)?", text)
    if not match:
        return None
    value = float(match.group(1))
    if value < 100:
        return None
    return value


async def query_analyzer(state: AgentState) -> AgentState:
    start = perf_counter()
    query = state["query"]
    lowered = query.lower()
    needs_order_id = any(
        word in lowered for word in ("订单", "退款", "退货", "物流", "快递")
    )
    analysis: dict[str, Any] = {
        "order_id": _extract_first_int(query) if needs_order_id else None,
        "budget": _extract_budget(query),
        "category": None,
        "keyword": query,
    }

    if any(word in lowered for word in ("手机", "拍照", "游戏")):
        analysis["category"] = "phone"
    elif any(word in lowered for word in ("电脑", "笔记本")):
        analysis["category"] = "laptop"
    elif any(word in lowered for word in ("耳机", "音频")):
        analysis["category"] = "audio"
    elif "平板" in lowered:
        analysis["category"] = "tablet"

    state["analysis"] = analysis
    add_step(
        state,
        "query_analyzer",
        {"query": query, "intent": state["intent"]},
        analysis,
        elapsed_ms(start),
    )
    return state
