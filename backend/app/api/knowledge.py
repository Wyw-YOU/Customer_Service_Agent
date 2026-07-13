"""
Knowledge API router.
  POST /api/knowledge/upload  — upload and index a document (CS / ADMIN only)
  GET  /api/knowledge/{id}    — query indexing status (authenticated users)
"""
from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import get_current_user, require_role
from app.config.database import get_db
from app.schemas.knowledge import KnowledgeUploadRequest, KnowledgeStatusResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/upload", response_model=KnowledgeStatusResponse)
async def upload_knowledge(
    request: KnowledgeUploadRequest,
    user: dict = Depends(require_role("CUSTOMER_SERVICE")),
    db=Depends(get_db),
):
    """Upload a markdown/text document, chunk it, embed, and index into Qdrant."""
    service = KnowledgeService(db)
    return await service.upload(request)


@router.get("/{doc_id}", response_model=KnowledgeStatusResponse)
async def get_knowledge_status(
    doc_id: int,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Get the indexing status and chunk count of a knowledge document."""
    service = KnowledgeService(db)
    result = await service.get_status(doc_id)
    if result is None:
        raise HTTPException(status_code=404, detail="知识文档不存在")
    return result
