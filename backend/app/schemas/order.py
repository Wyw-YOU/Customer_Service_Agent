from datetime import datetime
from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class LogisticsResponse(BaseModel):
    company: str
    tracking_no: str
    status: str
    location: str | None = None

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_no: str
    status: str
    payment_status: str
    total_amount: float
    created_at: datetime | None = None
    items: list[OrderItemResponse] = []
    logistics: LogisticsResponse | None = None

    model_config = {"from_attributes": True}


class RefundRequest(BaseModel):
    order_id: int
    reason: str


class RefundResponse(BaseModel):
    id: int
    order_id: int
    status: str

    model_config = {"from_attributes": True}
