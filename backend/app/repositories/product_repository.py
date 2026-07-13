from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductSpec, ProductTag


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def list(
        self,
        category: str | None = None,
        max_price: float | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        q = select(Product)
        if category:
            q = q.where(Product.category == category)
        if max_price is not None:
            q = q.where(Product.price <= max_price)
        q = q.where(Product.status == "ACTIVE").limit(limit).offset(offset)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def search(
        self,
        keyword: str | None = None,
        budget: float | None = None,
        category: str | None = None,
        limit: int = 10,
    ) -> list[Product]:
        q = select(Product).where(Product.status == "ACTIVE")
        if keyword:
            q = q.where(
                Product.name.ilike(f"%{keyword}%") |
                Product.brand.ilike(f"%{keyword}%") |
                Product.description.ilike(f"%{keyword}%")
            )
        if budget is not None:
            q = q.where(Product.price <= budget)
        if category:
            q = q.where(Product.category == category)
        q = q.limit(limit)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_specs(self, product_id: int) -> ProductSpec | None:
        q = select(ProductSpec).where(ProductSpec.product_id == product_id)
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def get_tags(self, product_id: int) -> list[str]:
        q = select(ProductTag.tag).where(ProductTag.product_id == product_id)
        result = await self.session.execute(q)
        return list(result.scalars().all())
