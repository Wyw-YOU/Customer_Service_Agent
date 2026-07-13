import pytest

from app.agent.graph import run_agent
from app.agent.state import create_initial_state
from app.config import settings as settings_module


@pytest.mark.asyncio
async def test_agent_workflow_returns_local_handoff_without_external_services(monkeypatch):
    monkeypatch.setattr(settings_module.settings, "llm_api_key", "")

    state = create_initial_state(user_id=101, query="我要投诉并转人工客服")

    result = await run_agent(state)

    assert result["intent"] == "COMPLAINT"
    assert result["need_human"] is True
    assert result["risk_level"] == "HIGH"
    assert "人工客服" in result["response"]
    assert [step["node_name"] for step in result["trace_steps"]] == [
        "intent_router",
        "query_analyzer",
        "human_handoff",
        "response_generator",
    ]
    assert "db_session" not in result["memory"]


@pytest.mark.asyncio
async def test_agent_workflow_handles_missing_runtime_session(monkeypatch):
    monkeypatch.setattr(settings_module.settings, "llm_api_key", "")

    state = create_initial_state(user_id=101, query="预算5000以内推荐拍照手机")

    result = await run_agent(state)

    assert result["intent"] == "PRODUCT_RECOMMEND"
    assert result["tool_results"]["product_search"]["success"] is False
    assert result["tool_results"]["product_search"]["error"]["code"] == "RUNTIME_ERROR"
    assert "暂时无法查询商品" in result["response"]
    assert "db_session" not in result["memory"]
