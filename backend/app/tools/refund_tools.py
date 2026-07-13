from sqlalchemy.ext.asyncio import AsyncSession

from app.services.order_service import OrderService
from app.services.refund_service import RefundService
from app.tools.common import ToolResult, tool_error, tool_success
from app.tools.order_tools import _validate_user_id


async def create_refund_tool(
    session: AsyncSession,
    user_id: int,
    order_id: int,
    reason: str,
) -> ToolResult:
    user_error = _validate_user_id(user_id)
    if user_error:
        return user_error

    if not reason or not reason.strip():
        return tool_error("INVALID_ARGUMENT", "Refund reason is required")

    try:
        order = await OrderService(session).get_order(order_id=order_id, user_id=user_id)
        if not order:
            return tool_error("NOT_FOUND", "Order not found", {"order_id": order_id})

        refund = await RefundService(session).create_refund(
            order_id=order.id,
            user_id=user_id,
            reason=reason.strip(),
            amount=order.total_amount,
            order_status=order.status,
            payment_status=order.payment_status,
        )
        return tool_success(refund)
    except ValueError as exc:
        return tool_error("BUSINESS_ERROR", str(exc), {"order_id": order_id})
    except Exception as exc:
        return tool_error("TOOL_ERROR", "Failed to create refund", {"reason": str(exc)})


class RefundTools:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refund(self, user_id: int, order_id: int, reason: str) -> ToolResult:
        return await create_refund_tool(
            self.session,
            user_id=user_id,
            order_id=order_id,
            reason=reason,
        )

