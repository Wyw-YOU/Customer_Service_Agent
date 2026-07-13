"""Pydantic schemas for knowledge document management API."""
from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from typing import Literal


class KnowledgeUploadRequest(BaseModel):
    """Request body for uploading a knowledge document."""
    name: str = Field(min_length=1, max_length=128)
    type: Literal["FAQ", "PRODUCT", "POLICY", "REVIEW"]
    content: str = Field(min_length=1, max_length=200_000)

    @field_validator("name", "content")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped


class KnowledgeStatusResponse(BaseModel):
    """Response after upload or when querying document status."""
    id: int
    name: str
    type: str
    status: str          # PENDING, INDEXED, ERROR
    chunk_count: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
