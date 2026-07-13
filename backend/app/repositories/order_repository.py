from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Logistics, Order, OrderItem


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: int) -> Order | None:
        q = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items), selectinload(Order.logistics))
        )
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int, limit: int = 20) -> list[Order]:
        q = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items), selectinload(Order.logistics))
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(q)
        return list(result.scalars().all())
