from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel


class ToolTrace(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    success: bool
    result: Any | None = None
    error: str | None = None
    started_at: datetime
    duration_ms: float