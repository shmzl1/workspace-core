"""Asynchronous model gateway contracts; no provider or HTTP client is implemented here."""

from typing import Any, Protocol

from pydantic import BaseModel, Field

from app.agents.shared.model_errors import (
    ModelGatewayConfigurationError,
    ModelGatewayDisabledError,
    ModelGatewayUnavailableError,
)


class ModelGatewayInput(BaseModel):
    task_name: str
    system_context: dict[str, Any] = Field(default_factory=dict)
    structured_input: dict[str, Any] = Field(default_factory=dict)
    output_schema_name: str


class ModelGatewayOutput(BaseModel):
    structured_output: dict[str, Any] = Field(default_factory=dict)
    model_name: str | None = None
    fallback_used: bool = False


class ModelGatewayStatus(BaseModel):
    enabled: bool
    configured: bool
    ready: bool
    provider: str
    model_name: str | None = None
    mode: str
    last_error: str | None = None


class ModelGateway(Protocol):
    async def generate(self, request: ModelGatewayInput) -> ModelGatewayOutput: ...

    async def get_status(self) -> ModelGatewayStatus: ...

    async def aclose(self) -> None: ...


class DisabledModelGateway:
    def __init__(self, provider: str = "openai_compatible") -> None:
        self.provider = provider

    async def generate(self, request: ModelGatewayInput) -> ModelGatewayOutput:
        del request
        raise ModelGatewayDisabledError("模型能力当前已禁用。")

    async def get_status(self) -> ModelGatewayStatus:
        return ModelGatewayStatus(
            enabled=False,
            configured=False,
            ready=False,
            provider=self.provider,
            model_name=None,
            mode="DISABLED",
        )

    async def aclose(self) -> None:
        return None


class NotImplementedModelGateway:
    def __init__(
        self,
        provider: str,
        model_name: str | None,
        *,
        configured: bool = True,
    ) -> None:
        self.provider = provider
        self.model_name = model_name
        self.configured = configured

    async def generate(self, request: ModelGatewayInput) -> ModelGatewayOutput:
        del request
        if not self.configured:
            raise ModelGatewayConfigurationError("模型能力已启用，但配置不完整。")
        raise ModelGatewayUnavailableError("模型 Provider 尚未实现。")

    async def get_status(self) -> ModelGatewayStatus:
        return ModelGatewayStatus(
            enabled=True,
            configured=self.configured,
            ready=False,
            provider=self.provider,
            model_name=self.model_name if self.configured else None,
            mode="NOT_IMPLEMENTED" if self.configured else "MISCONFIGURED",
        )

    async def aclose(self) -> None:
        return None
