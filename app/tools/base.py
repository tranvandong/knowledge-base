from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel


InputModelT = TypeVar("InputModelT", bound=BaseModel)


class BaseTool(ABC, Generic[InputModelT]):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def input_model(self) -> type[InputModelT]:
        pass

    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_model.model_json_schema(),
            },
        }

    def validate_arguments(
        self,
        arguments: dict[str, Any],
    ) -> InputModelT:
        return self.input_model.model_validate(arguments)

    @abstractmethod
    def execute(self, arguments: InputModelT) -> Any:
        pass