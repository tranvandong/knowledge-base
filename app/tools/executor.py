import time
from datetime import datetime, timezone
from typing import Any

from app.tools.errors import ToolError
from app.tools.registry import ToolRegistry
from app.tools.tracing import ToolTrace


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        
    def definitions(self) -> list[dict[str, Any]]:
        return self.registry.definitions()

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> tuple[Any | None, ToolTrace]:
        started_at = datetime.now(timezone.utc)
        started_time = time.perf_counter()

        try:
            result = self.registry.execute(
                name=name,
                arguments=arguments,
            )

            trace = ToolTrace(
                tool_name=name,
                arguments=arguments,
                success=True,
                result=result,
                started_at=started_at,
                duration_ms=self._duration_ms(started_time),
            )

            return result, trace

        except ToolError as exc:
            trace = ToolTrace(
                tool_name=name,
                arguments=arguments,
                success=False,
                error=str(exc),
                started_at=started_at,
                duration_ms=self._duration_ms(started_time),
            )

            return None, trace

    def _duration_ms(self, started_time: float) -> float:
        return round(
            (time.perf_counter() - started_time) * 1000,
            2,
        )