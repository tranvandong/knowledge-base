from typing import Any

from pydantic import ValidationError

from app.tools.base import BaseTool
from app.tools.errors import (
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolValidationError,
)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool[Any]] = {}

    def register(self, tool: BaseTool[Any]) -> None:
        if tool.name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool.name}"
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool[Any] | None:
        return self._tools.get(name)

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        tool = self.get(name)

        if tool is None:
            raise ToolNotFoundError(
                f"Tool '{name}' was not found"
            )

        try:
            validated_arguments = tool.validate_arguments(
                arguments
            )
        except ValidationError as exc:
            raise ToolValidationError(
                f"Invalid arguments for tool '{name}'"
            ) from exc

        try:
            return tool.execute(validated_arguments)
        except ToolError:
            raise
        except Exception as exc:
            raise ToolExecutionError(
                f"Tool '{name}' execution failed"
            ) from exc

    def definitions(self) -> list[dict[str, Any]]:
        return [
            tool.definition()
            for tool in self._tools.values()
        ]