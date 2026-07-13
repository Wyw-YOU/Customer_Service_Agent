from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, utcnow


class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("conversations.id"))
    query: Mapped[str] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="RUNNING")
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column(Float)

    steps: Mapped[list["AgentStep"]] = relationship(back_populates="run")
    tool_logs: Mapped[list["ToolLog"]] = relationship(back_populates="run")


class AgentStep(Base, TimestampMixin):
    __tablename__ = "agent_steps"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("agent_runs.id"))
    node_name: Mapped[str] = mapped_column(String(64))
    input_data: Mapped[dict | None] = mapped_column(JSONB, name="input")
    output_data: Mapped[dict | None] = mapped_column(JSONB, name="output")
    duration_ms: Mapped[int | None] = mapped_column(Integer, name="duration")

    run: Mapped["AgentRun"] = relationship(back_populates="steps")


class ToolLog(Base, TimestampMixin):
    __tablename__ = "tool_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("agent_runs.id"))
    tool_name: Mapped[str] = mapped_column(String(64))
    input_data: Mapped[dict | None] = mapped_column(JSONB, name="input")
    output_data: Mapped[dict | None] = mapped_column(JSONB, name="output")
    status: Mapped[str] = mapped_column(String(32))  # success, error
    latency_ms: Mapped[int | None] = mapped_column(Integer, name="latency")

    run: Mapped["AgentRun"] = relationship(back_populates="tool_logs")
