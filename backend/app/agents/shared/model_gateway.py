"""Asynchronous model gateway contracts and OpenAI-compatible implementation."""

import asyncio
import json
import re
from time import perf_counter
from typing import Any, Literal, Protocol

import httpx
from pydantic import BaseModel, Field
from pydantic import SecretStr

from app.agents.shared.model_errors import (
    ModelGatewayConfigurationError,
    ModelGatewayDisabledError,
    ModelGatewayOutputError,
    ModelGatewayUnavailableError,
)


class ModelGatewayInput(BaseModel):
    task_name: str
    system_context: dict[str, Any] = Field(default_factory=dict)
    structured_input: dict[str, Any] = Field(default_factory=dict)
    output_schema_name: str
    thinking_type: Literal["enabled", "disabled", "auto"] | None = None
    max_completion_tokens: int | None = Field(default=None, gt=0)


class ModelGatewayOutput(BaseModel):
    structured_output: dict[str, Any] = Field(default_factory=dict)
    provider: str | None = None
    model_name: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
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
            mode="DEGRADED" if self.configured else "MISCONFIGURED",
            last_error="MODEL_PROVIDER_NOT_IMPLEMENTED" if self.configured else "MODEL_CONFIGURATION_INCOMPLETE",
        )

    async def aclose(self) -> None:
        return None


class OpenAICompatibleModelGateway:
    """Minimal Chat Completions client with bounded retries and safe status."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: SecretStr,
        model_name: str,
        provider: str = "openai_compatible",
        timeout_seconds: float = 30,
        max_retries: int = 2,
        temperature: float = 0.2,
        proxy_url: SecretStr | None = None,
        trust_env: bool = True,
    ) -> None:
        self.provider = provider
        self.model_name = model_name
        self._base_url = base_url.strip()
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._temperature = temperature
        self._proxy_url = proxy_url.get_secret_value().strip() if proxy_url else ""
        self._trust_env = trust_env
        self._client: httpx.AsyncClient | None = None
        self._ready = False
        self._last_error: str | None = None

    async def generate(self, request: ModelGatewayInput) -> ModelGatewayOutput:
        if not self._configured:
            raise ModelGatewayConfigurationError("模型能力已启用，但配置不完整。")
        started_at = perf_counter()
        payload = {
            "model": self.model_name,
            "temperature": self._temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": str(request.system_context.get("prompt", "只输出符合要求的 JSON。")),
                },
                {
                    "role": "user",
                    "content": json.dumps(request.structured_input, ensure_ascii=False, separators=(",", ":")),
                },
            ],
        }
        if request.thinking_type is not None:
            payload["thinking"] = {"type": request.thinking_type}
        if request.max_completion_tokens is not None:
            payload["max_completion_tokens"] = request.max_completion_tokens
        response: httpx.Response | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._get_client().post(
                    self._endpoint,
                    headers={"Authorization": f"Bearer {self._api_key.get_secret_value()}"},
                    json=payload,
                )
            except httpx.TimeoutException as exc:
                if attempt < self._max_retries:
                    await asyncio.sleep(min(0.25 * (2 ** attempt), 1.0))
                    continue
                self._mark_degraded("MODEL_PROVIDER_TIMEOUT")
                raise ModelGatewayUnavailableError("模型服务响应超时。") from exc
            except (httpx.ConnectError, httpx.ProxyError) as exc:
                if attempt < self._max_retries:
                    await asyncio.sleep(min(0.25 * (2 ** attempt), 1.0))
                    continue
                self._mark_degraded("MODEL_PROVIDER_CONNECT_FAILED")
                raise ModelGatewayUnavailableError(
                    "模型服务连接失败，请检查 LLM_PROXY_URL 与 LLM_TRUST_ENV 配置。"
                ) from exc
            if response.status_code == 429 or response.status_code >= 500:
                if attempt < self._max_retries:
                    await asyncio.sleep(min(0.25 * (2 ** attempt), 1.0))
                    continue
                self._mark_degraded(f"MODEL_PROVIDER_HTTP_{response.status_code}")
                raise ModelGatewayUnavailableError("模型服务暂时不可用。")
            if response.status_code >= 400:
                self._mark_degraded(f"MODEL_PROVIDER_HTTP_{response.status_code}")
                raise ModelGatewayUnavailableError(f"模型服务拒绝请求（HTTP {response.status_code}）。")
            break
        if response is None:
            self._mark_degraded("MODEL_PROVIDER_NO_RESPONSE")
            raise ModelGatewayUnavailableError("模型服务未返回响应。")
        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            structured_output = _parse_json_object(content)
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._mark_degraded("MODEL_OUTPUT_INVALID")
            raise ModelGatewayOutputError("模型返回内容不符合 JSON 对象契约。") from exc
        usage = body.get("usage") if isinstance(body, dict) else None
        usage = usage if isinstance(usage, dict) else {}
        self._ready = True
        self._last_error = None
        return ModelGatewayOutput(
            structured_output=structured_output,
            provider=self.provider,
            model_name=self.model_name,
            duration_ms=max(0, int((perf_counter() - started_at) * 1000)),
            prompt_tokens=_optional_non_negative_int(usage.get("prompt_tokens")),
            completion_tokens=_optional_non_negative_int(usage.get("completion_tokens")),
            total_tokens=_optional_non_negative_int(usage.get("total_tokens")),
            fallback_used=False,
        )

    async def get_status(self) -> ModelGatewayStatus:
        if not self._configured:
            return ModelGatewayStatus(
                enabled=True,
                configured=False,
                ready=False,
                provider=self.provider,
                model_name=None,
                mode="MISCONFIGURED",
                last_error="MODEL_CONFIGURATION_INCOMPLETE",
            )
        mode = "READY" if self._ready else "DEGRADED" if self._last_error else "CONFIGURED"
        return ModelGatewayStatus(
            enabled=True,
            configured=True,
            ready=self._ready,
            provider=self.provider,
            model_name=self.model_name,
            mode=mode,
            last_error=self._last_error,
        )

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def mark_output_error(self) -> None:
        self._mark_degraded("MODEL_OUTPUT_SCHEMA_INVALID")

    @property
    def _configured(self) -> bool:
        return bool(
            self._base_url
            and self._api_key.get_secret_value().strip()
            and self.model_name.strip()
        )

    @property
    def _endpoint(self) -> str:
        return f"{self._base_url.rstrip('/')}/chat/completions"

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout_seconds),
                proxy=self._proxy_url or None,
                trust_env=self._trust_env,
            )
        return self._client

    def _mark_degraded(self, error_code: str) -> None:
        self._ready = False
        self._last_error = error_code


def _parse_json_object(content: Any) -> dict[str, Any]:
    if not isinstance(content, str):
        raise ValueError("model content is not text")
    value = content.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", value, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        value = fenced.group(1).strip()
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("model output is not an object")
    return parsed


def _optional_non_negative_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None
