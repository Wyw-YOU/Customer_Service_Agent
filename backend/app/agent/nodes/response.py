"""Response generation node."""

from time import perf_counter

from openai import AsyncOpenAI

from app.agent.nodes.common import add_step, elapsed_ms
from app.agent.runtime import AgentRuntime
from app.agent.state import AgentState
from app.config.settings import settings
from app.utils.logger import logger

CUSTOMER_SERVICE_PROMPT = """你是一个专业的数码商城 AI 客服助手。

规则：
1. 商品、订单、退款信息必须基于工具或知识库结果，不要编造。
2. 订单和退款必须遵守当前用户权限。
3. 退款只创建人工审批任务，不直接执行真实退款。
4. 如果工具或知识库没有结果，如实说明并建议补充信息或联系人工客服。
"""

NO_CONTEXT_NOTICE = "暂无相关知识库内容。"


def create_response_generator(runtime: AgentRuntime):
    async def response_generator(state: AgentState) -> AgentState:
        start = perf_counter()
        answer = _fallback_answer(state)
        llm_error: str | None = None

        should_call_llm = bool(settings.llm_api_key) and not (
            state["need_human"] and state["intent"] == "COMPLAINT"
        )
        if should_call_llm:
            try:
                llm = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
                response = await llm.chat.completions.create(
                    model=settings.llm_model,
                    messages=[
                        {"role": "system", "content": CUSTOMER_SERVICE_PROMPT},
                        {"role": "user", "content": _build_llm_user_content(state)},
                    ],
                    temperature=0.4,
                    max_tokens=1024,
                )
                answer = response.choices[0].message.content or answer
            except Exception as exc:
                logger.exception("LLM response generation failed in agent workflow")
                llm_error = str(exc)
                state["errors"].append({"node": "response_generator", "error": llm_error})

        state["response"] = answer
        add_step(
            state,
            "response_generator",
            {"intent": state["intent"], "has_context": bool(state["rag_context"])},
            {"answer_preview": answer[:200], "error": llm_error},
            elapsed_ms(start),
        )
        return state

    return response_generator


def _build_llm_user_content(state: AgentState) -> str:
    return (
        f"用户问题：{state['query']}\n"
        f"意图：{state['intent']}\n"
        f"工具结果：{state['tool_results']}\n"
        f"知识库：{state['rag_context'] or NO_CONTEXT_NOTICE}\n"
        "请给出简洁、可信、面向用户的中文回复。"
    )


def _fallback_answer(state: AgentState) -> str:
    if state["need_human"] and state["intent"] == "COMPLAINT":
        return "我已经识别到这是需要人工处理的问题，建议转接人工客服继续跟进。"

    if "product_search" in state["tool_results"]:
        return _format_product_answer(state["tool_results"]["product_search"])

    for key in ("order_query", "order_list"):
        if key in state["tool_results"]:
            result = state["tool_results"][key]
            if not result.get("success"):
                return _tool_failure_answer("暂时无法查询订单", result)
            return f"已查询到订单信息：{result.get('data')}"

    if "refund_create" in state["tool_results"]:
        result = state["tool_results"]["refund_create"]
        if not result.get("success"):
            return _tool_failure_answer("退款申请暂未创建", result, "请检查订单信息")
        return f"退款申请已创建，将进入人工审批流程：{result.get('data')}"

    if state["rag_context"]:
        return f"根据知识库资料：\n{state['rag_context'][:800]}"

    return (
        "我暂时没有找到足够的信息来准确回答。"
        "你可以补充商品、订单号或售后原因，我会继续帮你处理。"
    )


def _format_product_answer(result: dict) -> str:
    if not result.get("success"):
        return _tool_failure_answer("暂时无法查询商品", result)

    products = result.get("data") or []
    if not products:
        return "暂时没有找到符合条件的商品，可以放宽预算、品牌或品类后再试。"

    lines = ["我根据当前商品数据找到这些候选："]
    for item in products[:5]:
        description = item.get("description") or "暂无描述"
        lines.append(f"- {item.get('name')}：{item.get('price')} 元，{description}")
    return "\n".join(lines)


def _tool_failure_answer(prefix: str, result: dict, default: str = "工具调用失败") -> str:
    message = (result.get("error") or {}).get("message", default)
    return f"{prefix}：{message}"
