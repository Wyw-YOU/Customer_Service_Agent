from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.jwt import require_role
from app.config.database import get_db
from app.schemas.admin import (
    ApprovalAction,
    ApprovalActionResponse,
    ApprovalResponse,
    ConversationDetailResponse,
    ConversationSummaryResponse,
    TraceResponse,
    UserSummaryResponse,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/traces", response_model=list[TraceResponse])
async def list_traces(
    status: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = AdminService(db)
    return await service.list_traces(status=status, limit=limit, offset=offset)


@router.get("/traces/{run_id}", response_model=TraceResponse)
async def get_trace(
    run_id: int,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = AdminService(db)
    trace = await service.get_trace(run_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace


@router.get("/approvals", response_model=list[ApprovalResponse])
async def list_approvals(
    status: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = AdminService(db)
    return await service.list_approvals(status=status, limit=limit, offset=offset)


@router.get("/conversations", response_model=list[ConversationSummaryResponse])
async def list_conversations(
    status: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = AdminService(db)
    return await service.list_conversations(status=status, limit=limit, offset=offset)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = AdminService(db)
    conversation = await service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/users", response_model=list[UserSummaryResponse])
async def list_users(
    role: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    user: dict = Depends(require_role("ADMIN")),
    db=Depends(get_db),
):
    service = AdminService(db)
    return await service.list_users(role=role, limit=limit, offset=offset)


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalActionResponse)
async def approve(
    approval_id: int,
    request: ApprovalAction | None = None,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = AdminService(db)
    try:
        comment = request.comment if request else None
        return await service.approve(approval_id, int(user["sub"]), comment)
    except ValueError as e:
        status_code = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalActionResponse)
async def reject(
    approval_id: int,
    request: ApprovalAction | None = None,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    service = AdminService(db)
    try:
        comment = request.comment if request else None
        return await service.reject(approval_id, int(user["sub"]), comment)
    except ValueError as e:
        status_code = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
