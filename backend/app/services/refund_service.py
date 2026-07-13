from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.refund_repository import RefundRepository
from app.schemas.order import RefundResponse


class RefundService:
    def __init__(self, session: AsyncSession):
        self.repo = RefundRepository(session)

    async def create_refund(self, order_id: int, user_id: int, reason: str, amount: float) -> RefundResponse:
        refund = await self.repo.create(order_id, user_id, reason, amount)
        await self.repo.create_approval(refund)
        return RefundResponse(id=refund.id, order_id=refund.order_id, status=refund.status)
