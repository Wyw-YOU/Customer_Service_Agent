from pydantic import BaseModel, Field


class ProductSearchRequest(BaseModel):
    keyword: str | None = None
    budget: float | None = Field(default=None, ge=0)
    category: str | None = None


class ProductSpecResponse(BaseModel):
    cpu: str | None = None
    gpu: str | None = None
    screen: str | None = None
    camera: str | None = None
    battery: str | None = None
    weight: str | None = None
    os: str | None = None

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: float
    stock: int
    description: str | None = None
    image_url: str | None = None
    specs: ProductSpecResponse | None = None
    tags: list[str] = []

    model_config = {"from_attributes": True}
