"""Shared helpers for agent graph nodes."""

from time import perf_counter
from typing import Any

from app.agent.state import AgentState


def add_step(
    state: AgentState,
    node_name: str,
    input_data: dict[str, Any] | None,
    output_data: dict[str, Any] | None,
    duration_ms: int,
) -> None:
    state["trace_steps"].append(
        {
            "node_name": node_name,
            "input_data": input_data,
            "output_data": output_data,
            "duration_ms": duration_ms,
        }
    )


def elapsed_ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)
