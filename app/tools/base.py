from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Tên duy nhất của tool.
        """
        pass

    @abstractmethod
    def definition(self) -> dict[str, Any]:
        """
        JSON Schema gửi cho LLM.
        """
        pass

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> Any:
        """
        Thực thi tool sau khi LLM yêu cầu.
        """
        pass