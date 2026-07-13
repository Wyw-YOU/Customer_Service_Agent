from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import get_current_user
from app.config.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    service = AgentService(db)
    try:
        return await service.chat(user_id=int(user["sub"]), request=request)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
