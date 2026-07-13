from sqlalchemy.ext.asyncio import AsyncSession

from app.services.order_service import OrderService
from app.tools.common import ToolResult, tool_error, tool_success


def _validate_user_id(user_id: int | None) -> ToolResult | None:
    if user_id is None:
        return tool_error("AUTH_REQUIRED", "user_id is required")
    return None


async def get_order_tool(session: AsyncSession, user_id: int, order_id: int) -> ToolResult:
    user_error = _validate_user_id(user_id)
    if user_error:
        return user_error

    try:
        order = await OrderService(session).get_order(order_id=order_id, user_id=user_id)
        if not order:
            return tool_error("NOT_FOUND", "Order not found", {"order_id": order_id})
        return tool_success(order)
    except ValueError as exc:
        return tool_error("BUSINESS_ERROR", str(exc))
    except Exception as exc:
        return tool_error("TOOL_ERROR", "Failed to get order", {"reason": str(exc)})


async def list_user_orders_tool(session: AsyncSession, user_id: int) -> ToolResult:
    user_error = _validate_user_id(user_id)
    if user_error:
        return user_error

    try:
        orders = await OrderService(session).list_user_orders(user_id=user_id)
        return tool_success(orders)
    except ValueError as exc:
        return tool_error("BUSINESS_ERROR", str(exc))
    except Exception as exc:
        return tool_error("TOOL_ERROR", "Failed to list user orders", {"reason": str(exc)})


class OrderTools:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_order(self, user_id: int, order_id: int) -> ToolResult:
        return await get_order_tool(self.session, user_id=user_id, order_id=order_id)

    async def list_user_orders(self, user_id: int) -> ToolResult:
        return await list_user_orders_tool(self.session, user_id=user_id)

