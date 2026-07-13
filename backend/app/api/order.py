from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt import get_current_user
from app.config.database import get_db
from app.schemas.order import OrderResponse, RefundRequest, RefundResponse
from app.services.order_service import OrderService
from app.services.refund_service import RefundService

router = APIRouter(prefix="/api", tags=["orders"])


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, user: dict = Depends(get_current_user), db=Depends(get_db)):
    service = OrderService(db)
    order = await service.get_order(order_id, user_id=int(user["sub"]))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/users/me/orders", response_model=list[OrderResponse])
async def list_my_orders(user: dict = Depends(get_current_user), db=Depends(get_db)):
    service = OrderService(db)
    return await service.list_user_orders(user_id=int(user["sub"]))


@router.post("/refunds", response_model=RefundResponse)
async def create_refund(request: RefundRequest, user: dict = Depends(get_current_user), db=Depends(get_db)):
    order_service = OrderService(db)
    order = await order_service.get_order(request.order_id, user_id=int(user["sub"]))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    service = RefundService(db)
    return await service.create_refund(request.order_id, int(user["sub"]), request.reason, order.total_amount)
