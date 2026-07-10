"""Model gateway types only; this module performs no HTTP or credential access."""

from typing import Any, Protocol

from pydantic import BaseModel, Field


class ModelGatewayInput(BaseModel):
    task_name: str
    system_context: dict[str, Any] = Field(default_factory=dict)
    structured_input: dict[str, Any] = Field(default_factory=dict)
    output_schema_name: str


class ModelGatewayOutput(BaseModel):
    structured_output: dict[str, Any] = Field(default_factory=dict)
    model_name: str | None = None
    fallback_used: bool = False


class ModelGateway(Protocol):
    def generate(self, request: ModelGatewayInput) -> ModelGatewayOutput: ...
