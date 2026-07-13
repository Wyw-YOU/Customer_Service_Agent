from datetime import datetime
from pydantic import BaseModel


class TraceStepResponse(BaseModel):
    id: int
    node_name: str
    input_data: dict | None = None
    output_data: dict | None = None
    duration_ms: int | None = None

    model_config = {"from_attributes": True}


class TraceResponse(BaseModel):
    id: int
    conversation_id: int
    query: str
    intent: str | None = None
    status: str
    latency_ms: int | None = None
    confidence: float | None = None
    created_at: datetime | None = None
    steps: list[TraceStepResponse] = []

    model_config = {"from_attributes": True}


class ApprovalResponse(BaseModel):
    id: int
    type: str
    target_id: int
    risk_level: str
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ApprovalAction(BaseModel):
    action: str  # "approve" or "reject"
    comment: str | None = None
