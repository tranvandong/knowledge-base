import logging
import time
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.tools.errors import ToolError
from app.tools.registry import ToolRegistry
from app.tools.tracing import ToolTrace


logger = logging.getLogger(__name__)


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def definitions(self) -> list[dict[str, Any]]:
        return self.registry.definitions()

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        tool_call_id: str | None = None,
    ) -> tuple[Any | None, ToolTrace]:
        trace_id = uuid4()
        started_at = datetime.now(timezone.utc)
        started_time = time.perf_counter()

        logger.info(
            "Tool started | trace_id=%s | tool_call_id=%s | "
            "tool=%s | arguments=%s",
            trace_id,
            tool_call_id,
            name,
            arguments,
        )

        try:
            result = self.registry.execute(
                name=name,
                arguments=arguments,
            )

            trace = ToolTrace(
                trace_id=trace_id,
                tool_call_id=tool_call_id,
                tool_name=name,
                arguments=arguments,
                success=True,
                result=result,
                started_at=started_at,
                duration_ms=self._duration_ms(started_time),
            )

            logger.info(
                "Tool succeeded | trace_id=%s | tool=%s | "
                "duration_ms=%s",
                trace.trace_id,
                trace.tool_name,
                trace.duration_ms,
            )

            return result, trace

        except ToolError as exc:
            trace = ToolTrace(
                trace_id=trace_id,
                tool_call_id=tool_call_id,
                tool_name=name,
                arguments=arguments,
                success=False,
                error=str(exc),
                started_at=started_at,
                duration_ms=self._duration_ms(started_time),
            )

            logger.warning(
                "Tool failed | trace_id=%s | tool=%s | "
                "duration_ms=%s | error=%s",
                trace.trace_id,
                trace.tool_name,
                trace.duration_ms,
                trace.error,
            )

            return None, trace

    def _duration_ms(self, started_time: float) -> float:
        return round(
            (time.perf_counter() - started_time) * 1000,
            2,
        )