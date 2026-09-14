from typing import Any

from app.tools.base import BaseTool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        tool = self.get(name)

        if tool is None:
            raise ValueError(f"Tool not found: {name}")

        return tool.execute(arguments)

    def definitions(self) -> list[dict[str, Any]]:
        return [
            tool.definition()
            for tool in self._tools.values()
        ]