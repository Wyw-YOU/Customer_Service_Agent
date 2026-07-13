from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(String(128))
    phone: Mapped[str | None] = mapped_column(String(32))
    hashed_password: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(32), default="USER")  # USER, CUSTOMER_SERVICE, ADMIN
    is_active: Mapped[bool] = mapped_column(default=True)

    preferences: Mapped[list["UserPreference"]] = relationship(back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    preference_key: Mapped[str] = mapped_column(String(64))
    preference_value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    user: Mapped["User"] = relationship(back_populates="preferences")
