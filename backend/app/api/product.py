from fastapi import APIRouter, Depends, HTTPException, Query

from app.config.database import get_db
from app.schemas.product import ProductResponse, ProductSearchRequest
from app.services.product_service import ProductService

router = APIRouter(prefix="/api", tags=["products"])


@router.get("/products", response_model=list[ProductResponse])
async def list_products(
    category: str | None = Query(None),
    max_price: float | None = Query(None, ge=0),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
):
    service = ProductService(db)
    return await service.list_products(category, max_price, limit, offset)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db=Depends(get_db)):
    service = ProductService(db)
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products/search", response_model=list[ProductResponse])
async def search_products(request: ProductSearchRequest, db=Depends(get_db)):
    service = ProductService(db)
    return await service.search_products(request.keyword, request.budget, request.category)
