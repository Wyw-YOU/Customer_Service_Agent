from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductResponse, ProductSpecResponse


class ProductService:
    def __init__(self, session: AsyncSession):
        self.repo = ProductRepository(session)

    async def list_products(self, category: str | None = None, max_price: float | None = None,
                            limit: int = 20, offset: int = 0) -> list[ProductResponse]:
        products = await self.repo.list(category, max_price, limit, offset)
        return [await self._to_response(p) for p in products]

    async def search_products(self, keyword: str | None = None, budget: float | None = None,
                              category: str | None = None) -> list[ProductResponse]:
        products = await self.repo.search(keyword, budget, category)
        return [await self._to_response(p) for p in products]

    async def get_product(self, product_id: int) -> ProductResponse | None:
        product = await self.repo.get_by_id(product_id)
        if not product:
            return None
        return await self._to_response(product)

    async def _to_response(self, product) -> ProductResponse:
        specs = await self.repo.get_specs(product.id)
        tags = await self.repo.get_tags(product.id)
        return ProductResponse(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            price=product.price,
            stock=product.stock,
            description=product.description,
            image_url=product.image_url,
            specs=ProductSpecResponse.model_validate(specs) if specs else None,
            tags=tags,
        )
