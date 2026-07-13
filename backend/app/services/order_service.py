from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.order_repository import OrderRepository
from app.schemas.order import LogisticsResponse, OrderItemResponse, OrderResponse


class OrderService:
    def __init__(self, session: AsyncSession):
        self.repo = OrderRepository(session)

    async def get_order(self, order_id: int, user_id: int) -> OrderResponse | None:
        order = await self.repo.get_by_id(order_id)
        if not order:
            return None
        # Safety: verify user owns the order
        if order.user_id != user_id:
            return None
        return self._to_response(order)

    async def list_user_orders(self, user_id: int) -> list[OrderResponse]:
        orders = await self.repo.list_by_user(user_id)
        return [self._to_response(o) for o in orders]

    def _to_response(self, order) -> OrderResponse:
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            order_no=order.order_no,
            status=order.status,
            payment_status=order.payment_status,
            total_amount=order.total_amount,
            created_at=order.created_at,
            items=[OrderItemResponse(id=i.id, product_id=i.product_id, quantity=i.quantity, price=i.price)
                   for i in order.items],
            logistics=LogisticsResponse(
                company=order.logistics.company,
                tracking_no=order.logistics.tracking_no,
                status=order.logistics.status,
                location=order.logistics.location,
            ) if order.logistics else None,
        )
