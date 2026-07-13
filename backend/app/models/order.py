from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, utcnow


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    order_no: Mapped[str] = mapped_column(String(64), unique=True)
    status: Mapped[str] = mapped_column(String(32), default="CREATED")
    payment_status: Mapped[str] = mapped_column(String(32), default="PENDING")
    total_amount: Mapped[float] = mapped_column(Float)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    logistics: Mapped["Logistics | None"] = relationship(back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(Float)

    order: Mapped["Order"] = relationship(back_populates="items")


class Logistics(Base):
    __tablename__ = "logistics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("orders.id"), unique=True)
    company: Mapped[str] = mapped_column(String(64))
    tracking_no: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(64))  # IN_TRANSIT, DELIVERED, etc.
    location: Mapped[str | None] = mapped_column(String(128))
    timestamp = mapped_column(DateTime(timezone=True), default=utcnow)

    order: Mapped["Order"] = relationship(back_populates="logistics")
