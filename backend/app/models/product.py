from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, utcnow


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    brand: Mapped[str] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(64))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(512))

    specs: Mapped["ProductSpec"] = relationship(back_populates="product", uselist=False)
    tags: Mapped[list["ProductTag"]] = relationship(back_populates="product")


class ProductSpec(Base):
    __tablename__ = "product_specs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), unique=True)
    cpu: Mapped[str | None] = mapped_column(String(128))
    gpu: Mapped[str | None] = mapped_column(String(128))
    screen: Mapped[str | None] = mapped_column(String(128))
    camera: Mapped[str | None] = mapped_column(String(128))
    battery: Mapped[str | None] = mapped_column(String(128))
    weight: Mapped[str | None] = mapped_column(String(32))
    os: Mapped[str | None] = mapped_column(String(64))

    product: Mapped["Product"] = relationship(back_populates="specs")


class ProductTag(Base):
    __tablename__ = "product_tags"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    tag: Mapped[str] = mapped_column(String(64))

    product: Mapped["Product"] = relationship(back_populates="tags")
