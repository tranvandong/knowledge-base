from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ToolTrace(BaseModel):
    trace_id: UUID
    tool_call_id: str | None = None
    tool_name: str
    arguments: dict[str, Any]
    success: bool
    result: Any | None = None
    error: str | None = None
    started_at: datetime
    duration_ms: float