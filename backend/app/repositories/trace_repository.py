from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.agent import AgentRun, AgentStep, ToolLog


class TraceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_runs(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AgentRun]:
        q = (
            select(AgentRun)
            .order_by(AgentRun.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(selectinload(AgentRun.steps), selectinload(AgentRun.tool_logs))
        )
        if status:
            q = q.where(AgentRun.status == status)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_run(self, run_id: int) -> AgentRun | None:
        q = (
            select(AgentRun)
            .where(AgentRun.id == run_id)
            .options(selectinload(AgentRun.steps), selectinload(AgentRun.tool_logs))
        )
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def list_run_details(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        runs = await self.list_runs(status=status, limit=limit, offset=offset)
        return [self._to_detail(run) for run in runs]

    async def get_run_detail(self, run_id: int) -> dict | None:
        run = await self.get_run(run_id)
        if run is None:
            return None
        return self._to_detail(run)

    def _to_detail(self, run: AgentRun) -> dict:
        steps = [
            self._step_to_detail(step)
            for step in sorted(run.steps, key=lambda item: item.id)
        ]
        tool_logs = [
            self._tool_log_to_detail(log)
            for log in sorted(run.tool_logs, key=lambda item: item.id)
        ]
        return {
            "id": run.id,
            "conversation_id": run.conversation_id,
            "query": run.query,
            "intent": run.intent,
            "status": run.status,
            "latency_ms": run.latency_ms,
            "confidence": run.confidence,
            "created_at": run.created_at,
            "error_message": self._first_error(steps),
            "steps": steps,
            "tool_logs": tool_logs,
        }

    def _step_to_detail(self, step: AgentStep) -> dict:
        return {
            "id": step.id,
            "node_name": step.node_name,
            "input_data": step.input_data,
            "output_data": step.output_data,
            "duration_ms": step.duration_ms,
            "error_message": self._extract_error(step.output_data),
        }

    def _tool_log_to_detail(self, log: ToolLog) -> dict:
        return {
            "id": log.id,
            "tool_name": log.tool_name,
            "input_data": log.input_data,
            "output_data": log.output_data,
            "status": log.status,
            "latency_ms": log.latency_ms,
            "created_at": log.created_at,
            "error_message": self._extract_error(log.output_data),
        }

    def _first_error(self, steps: list[dict]) -> str | None:
        for step in steps:
            if step["error_message"]:
                return step["error_message"]
        return None

    def _extract_error(self, output_data: dict | None) -> str | None:
        if not output_data:
            return None
        error = output_data.get("error")
        if error is None:
            return None
        if isinstance(error, str):
            return error
        if isinstance(error, dict):
            message = error.get("message") or error.get("detail") or error.get("code")
            return str(message) if message else str(error)
        return str(error)
