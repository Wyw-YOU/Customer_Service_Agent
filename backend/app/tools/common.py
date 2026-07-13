from typing import Any

from pydantic import BaseModel

ToolResult = dict[str, Any]


def serialize_tool_data(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [serialize_tool_data(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_tool_data(item) for key, item in value.items()}
    return value


def tool_success(data: Any) -> ToolResult:
    return {"success": True, "data": serialize_tool_data(data), "error": None}


def tool_error(code: str, message: str, details: dict[str, Any] | None = None) -> ToolResult:
    error: dict[str, Any] = {"code": code, "message": message}
    if details:
        error["details"] = details
    return {"success": False, "data": None, "error": error}

