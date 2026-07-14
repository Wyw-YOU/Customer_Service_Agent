from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.aftersale import ApprovalTask, Refund
from app.models.order import Order
from app.models.user import User

ACTIVE_REFUND_STATUSES = {"PENDING_REVIEW", "APPROVED"}


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

    async def has_active_refund_for_order(self, order_id: int) -> bool:
        q = select(Refund.id).where(
            Refund.order_id == order_id,
            Refund.status.in_(ACTIVE_REFUND_STATUSES),
        )
        result = await self.session.execute(q)
        return result.scalar_one_or_none() is not None

    async def list_approvals(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ApprovalTask]:
        q = (
            select(ApprovalTask)
            .order_by(ApprovalTask.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if status:
            q = q.where(ApprovalTask.status == status)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def list_approval_details(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        requester = aliased(User)
        operator = aliased(User)
        q = (
            select(
                ApprovalTask,
                Refund,
                Order,
                requester.id.label("requester_id"),
                requester.username.label("requester_username"),
                operator.id.label("operator_user_id"),
                operator.username.label("operator_username"),
            )
            .outerjoin(
                Refund,
                and_(ApprovalTask.type == "REFUND", ApprovalTask.target_id == Refund.id),
            )
            .outerjoin(Order, Refund.order_id == Order.id)
            .outerjoin(requester, Refund.user_id == requester.id)
            .outerjoin(operator, ApprovalTask.operator_id == operator.id)
            .order_by(ApprovalTask.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if status:
            q = q.where(ApprovalTask.status == status)

        result = await self.session.execute(q)
        details: list[dict] = []
        for (
            task,
            refund,
            order,
            requester_id,
            requester_username,
            operator_id,
            operator_username,
        ) in result.all():
            details.append(
                {
                    "id": task.id,
                    "type": task.type,
                    "target_id": task.target_id,
                    "risk_level": task.risk_level,
                    "status": task.status,
                    "created_at": task.created_at,
                    "operator_id": operator_id,
                    "operator_username": operator_username,
                    "comment": task.comment,
                    "refund_id": refund.id if refund else None,
                    "refund_reason": refund.reason if refund else None,
                    "refund_amount": refund.amount if refund else None,
                    "refund_status": refund.status if refund else None,
                    "order_id": order.id if order else None,
                    "order_no": order.order_no if order else None,
                    "order_status": order.status if order else None,
                    "payment_status": order.payment_status if order else None,
                    "user_id": requester_id,
                    "username": requester_username,
                }
            )
        return details

    async def get_approval(self, approval_id: int) -> ApprovalTask | None:
        return await self.session.get(ApprovalTask, approval_id)

    async def create_approval(self, refund: Refund, risk_level: str = "HIGH") -> ApprovalTask:
        task = ApprovalTask(type="REFUND", target_id=refund.id, risk_level=risk_level)
        self.session.add(task)
        await self.session.flush()
        return task
