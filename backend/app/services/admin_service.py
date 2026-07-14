from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.admin_repository import AdminRepository
from app.repositories.refund_repository import RefundRepository
from app.repositories.trace_repository import TraceRepository


class AdminService:
    def __init__(self, session: AsyncSession):
        self.admin_repo = AdminRepository(session)
        self.refund_repo = RefundRepository(session)
        self.trace_repo = TraceRepository(session)

    async def list_approvals(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        return await self.refund_repo.list_approval_details(
            status=status,
            limit=limit,
            offset=offset,
        )

    async def approve(self, approval_id: int, operator_id: int, comment: str | None = None) -> dict:
        task = await self.refund_repo.get_approval(approval_id)
        if not task:
            raise ValueError("Approval task not found")
        if task.type != "REFUND":
            raise ValueError("Unsupported approval task type")
        if task.status != "PENDING":
            raise ValueError("Approval task already processed")
        task.status = "APPROVED"
        task.operator_id = operator_id
        task.comment = comment

        refund = await self.refund_repo.get_by_id(task.target_id)
        if not refund:
            raise ValueError("Refund not found")
        refund.status = "APPROVED"

        return {"id": task.id, "status": task.status, "comment": task.comment}

    async def reject(self, approval_id: int, operator_id: int, comment: str | None = None) -> dict:
        task = await self.refund_repo.get_approval(approval_id)
        if not task:
            raise ValueError("Approval task not found")
        if task.type != "REFUND":
            raise ValueError("Unsupported approval task type")
        if task.status != "PENDING":
            raise ValueError("Approval task already processed")
        task.status = "REJECTED"
        task.operator_id = operator_id
        task.comment = comment

        refund = await self.refund_repo.get_by_id(task.target_id)
        if not refund:
            raise ValueError("Refund not found")
        refund.status = "REJECTED"

        return {"id": task.id, "status": task.status, "comment": task.comment}

    async def list_traces(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        return await self.trace_repo.list_run_details(
            status=status,
            limit=limit,
            offset=offset,
        )

    async def get_trace(self, run_id: int):
        return await self.trace_repo.get_run_detail(run_id)

    async def list_conversations(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        return await self.admin_repo.list_conversations(
            status=status,
            limit=limit,
            offset=offset,
        )

    async def get_conversation(self, conversation_id: int):
        return await self.admin_repo.get_conversation_detail(conversation_id)

    async def list_users(
        self,
        role: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        return await self.admin_repo.list_users(role=role, limit=limit, offset=offset)
