"""Runtime dependencies for one agent graph invocation."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(slots=True)
class AgentRuntime:
    """Dependencies used by graph nodes but kept out of serializable state."""

    db_session: AsyncSession | None = None
