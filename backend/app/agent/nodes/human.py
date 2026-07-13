"""Human handoff node."""

from time import perf_counter

from app.agent.nodes.common import add_step, elapsed_ms
from app.agent.state import AgentState


async def human_node(state: AgentState) -> AgentState:
    start = perf_counter()
    state["need_human"] = True
    state["risk_level"] = "HIGH" if state["intent"] == "COMPLAINT" else "MEDIUM"
    add_step(
        state,
        "human_handoff",
        {"intent": state["intent"], "confidence": state["confidence"]},
        {"need_human": True, "risk_level": state["risk_level"]},
        elapsed_ms(start),
    )
    return state
