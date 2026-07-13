from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aftersale import ApprovalTask, Refund


class RefundRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order_id: int, user_id: int, reason: str, amount: float) -> Refund:
        refund = Refund(order_id=order_id, user_id=user_id, reason=reason, amount=amount)
        self.session.add(refund)
        await self.session.flush()
        return refund

    async def get_by_id(self, refund_id: int) -> Refund | None:
        return await self.session.get(Refund, refund_id)

    async def list_approvals(self, status: str | None = None) -> list[ApprovalTask]:
        q = select(ApprovalTask).order_by(ApprovalTask.created_at.desc())
        if status:
            q = q.where(ApprovalTask.status == status)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_approval(self, approval_id: int) -> ApprovalTask | None:
        return await self.session.get(ApprovalTask, approval_id)

    async def create_approval(self, refund: Refund, risk_level: str = "HIGH") -> ApprovalTask:
        task = ApprovalTask(type="REFUND", target_id=refund.id, risk_level=risk_level)
        self.session.add(task)
        await self.session.flush()
        return task
