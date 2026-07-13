from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.agent import AgentRun, AgentStep


class TraceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_runs(self, limit: int = 50) -> list[AgentRun]:
        q = select(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit).options(selectinload(AgentRun.steps))
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_run(self, run_id: int) -> AgentRun | None:
        q = select(AgentRun).where(AgentRun.id == run_id).options(selectinload(AgentRun.steps))
        result = await self.session.execute(q)
        return result.scalar_one_or_none()
