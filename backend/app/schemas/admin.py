from datetime import datetime

from pydantic import BaseModel


class TraceStepResponse(BaseModel):
    id: int
    node_name: str
    input_data: dict | None = None
    output_data: dict | None = None
    duration_ms: int | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class ToolLogResponse(BaseModel):
    id: int
    tool_name: str
    input_data: dict | None = None
    output_data: dict | None = None
    status: str
    latency_ms: int | None = None
    created_at: datetime | None = None
    error_message: str | None = None

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
    error_message: str | None = None
    steps: list[TraceStepResponse] = []
    tool_logs: list[ToolLogResponse] = []

    model_config = {"from_attributes": True}


class ApprovalResponse(BaseModel):
    id: int
    type: str
    target_id: int
    risk_level: str
    status: str
    created_at: datetime | None = None
    operator_id: int | None = None
    operator_username: str | None = None
    comment: str | None = None
    refund_id: int | None = None
    refund_reason: str | None = None
    refund_amount: float | None = None
    refund_status: str | None = None
    order_id: int | None = None
    order_no: str | None = None
    order_status: str | None = None
    payment_status: str | None = None
    user_id: int | None = None
    username: str | None = None

    model_config = {"from_attributes": True}


class ApprovalAction(BaseModel):
    comment: str | None = None


class ApprovalActionResponse(BaseModel):
    id: int
    status: str
    comment: str | None = None


class ConversationMessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    sources: str | None = None
    timestamp: datetime | None = None

    model_config = {"from_attributes": True}


class ConversationSummaryResponse(BaseModel):
    id: int
    user_id: int
    username: str
    user_email: str | None = None
    user_phone: str | None = None
    title: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_message_at: datetime | None = None
    last_message_role: str | None = None
    last_message_preview: str | None = None
    message_count: int = 0

    model_config = {"from_attributes": True}


class ConversationDetailResponse(ConversationSummaryResponse):
    messages: list[ConversationMessageResponse] = []


class UserSummaryResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    phone: str | None = None
    role: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
