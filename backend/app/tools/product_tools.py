from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.product_service import ProductService
from app.tools.common import ToolResult, tool_error, tool_success


async def list_products_tool(
    session: AsyncSession,
    category: str | None = None,
    max_price: float | None = None,
    limit: int = 20,
    offset: int = 0,
) -> ToolResult:
    try:
        products = await ProductService(session).list_products(
            category=category,
            max_price=max_price,
            limit=limit,
            offset=offset,
        )
        return tool_success(products)
    except ValueError as exc:
        return tool_error("BUSINESS_ERROR", str(exc))
    except Exception as exc:
        return tool_error("TOOL_ERROR", "Failed to list products", {"reason": str(exc)})


async def search_products_tool(
    session: AsyncSession,
    keyword: str | None = None,
    budget: float | None = None,
    category: str | None = None,
) -> ToolResult:
    try:
        products = await ProductService(session).search_products(
            keyword=keyword,
            budget=budget,
            category=category,
        )
        return tool_success(products)
    except ValueError as exc:
        return tool_error("BUSINESS_ERROR", str(exc))
    except Exception as exc:
        return tool_error("TOOL_ERROR", "Failed to search products", {"reason": str(exc)})


async def get_product_tool(session: AsyncSession, product_id: int) -> ToolResult:
    try:
        product = await ProductService(session).get_product(product_id)
        if not product:
            return tool_error("NOT_FOUND", "Product not found", {"product_id": product_id})
        return tool_success(product)
    except ValueError as exc:
        return tool_error("BUSINESS_ERROR", str(exc))
    except Exception as exc:
        return tool_error("TOOL_ERROR", "Failed to get product", {"reason": str(exc)})


class ProductTools:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_products(self, **kwargs: Any) -> ToolResult:
        return await list_products_tool(self.session, **kwargs)

    async def search_products(self, **kwargs: Any) -> ToolResult:
        return await search_products_tool(self.session, **kwargs)

    async def get_product(self, product_id: int) -> ToolResult:
        return await get_product_tool(self.session, product_id)

