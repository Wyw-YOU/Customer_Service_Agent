from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.refund_repository import RefundRepository
from app.schemas.order import RefundResponse


class RefundService:
    def __init__(self, session: AsyncSession):
        self.repo = RefundRepository(session)

    async def create_refund(
        self,
        order_id: int,
        user_id: int,
        reason: str,
        amount: float,
        order_status: str,
        payment_status: str,
    ) -> RefundResponse:
        if payment_status != "PAID":
            raise ValueError("Only paid orders can request refund")
        if order_status not in {"SHIPPING", "DELIVERED", "COMPLETED"}:
            raise ValueError("Order status does not allow refund")
        if await self.repo.has_active_refund_for_order(order_id):
            raise ValueError("Active refund already exists for this order")

        refund = await self.repo.create(order_id, user_id, reason, amount)
        await self.repo.create_approval(refund)
        return RefundResponse(id=refund.id, order_id=refund.order_id, status=refund.status)
