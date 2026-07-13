from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.refund_repository import RefundRepository
from app.repositories.trace_repository import TraceRepository


class ApprovalService:
    def __init__(self, session: AsyncSession):
        self.refund_repo = RefundRepository(session)
        self.trace_repo = TraceRepository(session)

    async def list_approvals(self, status: str | None = None):
        return await self.refund_repo.list_approvals(status)

    async def approve(self, approval_id: int, operator_id: int) -> dict:
        task = await self.refund_repo.get_approval(approval_id)
        if not task:
            raise ValueError("Approval task not found")
        task.status = "APPROVED"
        task.operator_id = operator_id

        refund = await self.refund_repo.get_by_id(task.target_id)
        if refund:
            refund.status = "APPROVED"

        return {"id": task.id, "status": task.status}

    async def reject(self, approval_id: int, operator_id: int) -> dict:
        task = await self.refund_repo.get_approval(approval_id)
        if not task:
            raise ValueError("Approval task not found")
        task.status = "REJECTED"
        task.operator_id = operator_id

        refund = await self.refund_repo.get_by_id(task.target_id)
        if refund:
            refund.status = "REJECTED"

        return {"id": task.id, "status": task.status}

    async def list_traces(self, limit: int = 50):
        return await self.trace_repo.list_runs(limit)

    async def get_trace(self, run_id: int):
        return await self.trace_repo.get_run(run_id)
