from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, utcnow


class Refund(Base, TimestampMixin):
    __tablename__ = "refunds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("orders.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    reason: Mapped[str] = mapped_column(Text)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="PENDING_REVIEW")


class ApprovalTask(Base, TimestampMixin):
    __tablename__ = "approval_tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(64))  # REFUND, etc.
    target_id: Mapped[int] = mapped_column(BigInteger)  # FK to refunds.id
    risk_level: Mapped[str] = mapped_column(String(32))  # LOW, MEDIUM, HIGH
    status: Mapped[str] = mapped_column(String(32), default="PENDING")  # PENDING, APPROVED, REJECTED
    operator_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))
    comment: Mapped[str | None] = mapped_column(Text)
