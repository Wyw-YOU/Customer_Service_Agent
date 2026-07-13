from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import get_current_user, require_role
from app.config.database import get_db
from app.schemas.admin import ApprovalResponse, TraceResponse
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/traces", response_model=list[TraceResponse])
async def list_traces(
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = ApprovalService(db)
    return await service.list_traces()


@router.get("/traces/{run_id}", response_model=TraceResponse)
async def get_trace(
    run_id: int,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = ApprovalService(db)
    trace = await service.get_trace(run_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace


@router.get("/approvals", response_model=list[ApprovalResponse])
async def list_approvals(
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = ApprovalService(db)
    return await service.list_approvals()


@router.post("/approvals/{approval_id}/approve")
async def approve(
    approval_id: int,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = ApprovalService(db)
    try:
        return await service.approve(approval_id, int(user["sub"]))
    except ValueError as e:
        status_code = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))


@router.post("/approvals/{approval_id}/reject")
async def reject(
    approval_id: int,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = ApprovalService(db)
    try:
        return await service.reject(approval_id, int(user["sub"]))
    except ValueError as e:
        status_code = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
