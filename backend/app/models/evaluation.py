from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, utcnow


class EvaluationDataset(Base, TimestampMixin):
    __tablename__ = "evaluation_dataset"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text)
    expected_intent: Mapped[str | None] = mapped_column(String(64))
    expected_answer: Mapped[str | None] = mapped_column(Text)
    expected_tool: Mapped[str | None] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(64))


class EvaluationResult(Base, TimestampMixin):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("agent_runs.id"))
    metric: Mapped[str] = mapped_column(String(64))
    score: Mapped[float] = mapped_column(Float)
