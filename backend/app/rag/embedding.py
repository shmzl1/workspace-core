"""Embedding provider clients with bounded retries and safe errors."""

import asyncio
import math
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

import httpx
from pydantic import SecretStr

from app.rag.errors import EmbeddingProviderError, KnowledgeBaseConfigurationError


_MULTIMODAL_HTTP_ERROR_CODES = {
    400: "MULTIMODAL_EMBEDDING_HTTP_400",
    401: "MULTIMODAL_EMBEDDING_HTTP_401",
    403: "MULTIMODAL_EMBEDDING_HTTP_403",
    404: "MULTIMODAL_EMBEDDING_HTTP_404",
    429: "MULTIMODAL_EMBEDDING_HTTP_429",
}


class EmbeddingClient(Protocol):
    model_name: str

    async def embed(self, texts: Sequence[str]) -> list[list[float]]: ...

    async def aclose(self) -> None: ...


class OpenAICompatibleEmbeddingClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: SecretStr,
        model_name: str,
        timeout_seconds: float,
        max_retries: int,
        batch_size: int = 32,
    ) -> None:
        self._base_url = base_url.strip()
        self._api_key = api_key
        self.model_name = model_name.strip()
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._batch_size = batch_size
        self._client: httpx.AsyncClient | None = None

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not self._configured:
            raise KnowledgeBaseConfigurationError("Embedding 配置不完整。")
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = list(texts[start:start + self._batch_size])
            if not batch:
                continue
            vectors.extend(await self._embed_batch(batch))
        if len(vectors) != len(texts):
            raise EmbeddingProviderError("Embedding 返回数量与输入数量不一致。")
        dimensions = {len(vector) for vector in vectors}
        if len(dimensions) > 1 or (vectors and next(iter(dimensions)) == 0):
            raise EmbeddingProviderError("Embedding 向量维度不一致。")
        return vectors

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        response: httpx.Response | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._get_client().post(
                    self._endpoint,
                    headers={"Authorization": f"Bearer {self._api_key.get_secret_value()}"},
                    json={"model": self.model_name, "input": texts},
                )
            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                if attempt < self._max_retries:
                    await asyncio.sleep(min(0.25 * (2 ** attempt), 1.0))
                    continue
                raise EmbeddingProviderError("Embedding 服务连接失败或超时。") from exc
            if response.status_code == 429 or response.status_code >= 500:
                if attempt < self._max_retries:
                    await asyncio.sleep(min(0.25 * (2 ** attempt), 1.0))
                    continue
                raise EmbeddingProviderError("Embedding 服务暂时不可用。")
            if response.status_code >= 400:
                raise EmbeddingProviderError(f"Embedding 服务拒绝请求（HTTP {response.status_code}）。")
            break
        if response is None:
            raise EmbeddingProviderError("Embedding 服务未返回响应。")
        try:
            payload = response.json()
            data = payload["data"]
            if not isinstance(data, list):
                raise TypeError
            ordered = sorted(data, key=lambda item: int(item.get("index", 0)))
            vectors = [self._vector(item.get("embedding")) for item in ordered]
        except (KeyError, TypeError, ValueError) as exc:
            raise EmbeddingProviderError("Embedding 返回结构无效。") from exc
        if len(vectors) != len(texts):
            raise EmbeddingProviderError("Embedding 返回数量与输入数量不一致。")
        return vectors

    @staticmethod
    def _vector(value: Any) -> list[float]:
        if not isinstance(value, list) or not value:
            raise TypeError
        vector = [float(item) for item in value]
        if not all(item == item and abs(item) != float("inf") for item in vector):
            raise ValueError
        return vector

    @property
    def _configured(self) -> bool:
        return bool(
            self._base_url
            and self._api_key.get_secret_value().strip()
            and self.model_name
        )

    @property
    def _endpoint(self) -> str:
        return f"{self._base_url.rstrip('/')}/embeddings"

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout_seconds)
        return self._client


class VolcengineMultimodalEmbeddingClient:
    """Text embedding client for Ark's dedicated multimodal endpoint."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: SecretStr,
        model_name: str,
        timeout_seconds: float,
        max_retries: int,
        batch_size: int = 1,
    ) -> None:
        self._base_url = base_url.strip()
        self._api_key = api_key
        self.model_name = model_name.strip()
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._batch_size = batch_size
        self._client: httpx.AsyncClient | None = None

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not self._configured:
            raise KnowledgeBaseConfigurationError("火山方舟多模态 Embedding 配置不完整。")
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise EmbeddingProviderError(
                "Embedding 输入必须是非空文本。",
                code="EMBEDDING_RESPONSE_INVALID",
            )

        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = list(texts[start:start + self._batch_size])
            batch_vectors = await asyncio.gather(
                *(self._embed_text(text) for text in batch)
            )
            vectors.extend(batch_vectors)

        if len(vectors) != len(texts):
            raise EmbeddingProviderError(
                "Embedding 返回数量与输入数量不一致。",
                code="EMBEDDING_RESPONSE_INVALID",
            )
        dimensions = {len(vector) for vector in vectors}
        if len(dimensions) > 1 or (vectors and next(iter(dimensions)) == 0):
            raise EmbeddingProviderError(
                "Embedding 向量维度不一致。",
                code="EMBEDDING_VECTOR_DIMENSION_INVALID",
            )
        return vectors

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _embed_text(self, text: str) -> list[float]:
        response = await self._post_with_retries(text)
        try:
            payload = response.json()
        except ValueError as exc:
            raise EmbeddingProviderError(
                "多模态 Embedding 返回结构无效。",
                code="EMBEDDING_RESPONSE_INVALID",
            ) from exc
        return parse_volcengine_multimodal_embedding_response(payload)

    async def _post_with_retries(self, text: str) -> httpx.Response:
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._get_client().post(
                    self._endpoint,
                    headers={
                        "Authorization": f"Bearer {self._api_key.get_secret_value()}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_name,
                        "input": [{"type": "text", "text": text}],
                    },
                )
            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                if attempt < self._max_retries:
                    await asyncio.sleep(min(0.25 * (2 ** attempt), 1.0))
                    continue
                raise EmbeddingProviderError(
                    "火山方舟多模态 Embedding 请求超时或连接失败。",
                    code="MULTIMODAL_EMBEDDING_TIMEOUT",
                ) from exc

            if response.status_code == 429 or response.status_code >= 500:
                if attempt < self._max_retries:
                    await asyncio.sleep(min(0.25 * (2 ** attempt), 1.0))
                    continue
            if response.status_code >= 400:
                raise EmbeddingProviderError(
                    "火山方舟多模态 Embedding 请求失败。",
                    code=_multimodal_http_error_code(response.status_code),
                )
            return response

        raise EmbeddingProviderError(
            "火山方舟多模态 Embedding 请求未返回响应。",
            code="MULTIMODAL_EMBEDDING_TIMEOUT",
        )

    @property
    def _configured(self) -> bool:
        return bool(
            self._base_url
            and self._api_key.get_secret_value().strip()
            and self.model_name
            and self._batch_size > 0
        )

    @property
    def _endpoint(self) -> str:
        return f"{self._base_url.rstrip('/')}/embeddings/multimodal"

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout_seconds)
        return self._client


def parse_volcengine_multimodal_embedding_response(payload: Any) -> list[float]:
    """Extract one dense vector from an Ark multimodal embedding response."""

    if not isinstance(payload, Mapping):
        raise _invalid_embedding_response()
    data = payload.get("data")
    if isinstance(data, Mapping):
        item = data
    elif isinstance(data, list) and len(data) == 1 and isinstance(data[0], Mapping):
        item = data[0]
    else:
        raise _invalid_embedding_response()

    embedding = item.get("embedding")
    if (
        isinstance(embedding, list)
        and len(embedding) == 1
        and isinstance(embedding[0], list)
    ):
        embedding = embedding[0]
    if not isinstance(embedding, list):
        raise _invalid_embedding_response()
    if not embedding or any(isinstance(value, (bool, list, dict)) for value in embedding):
        raise _invalid_vector_dimension()
    try:
        vector = [float(value) for value in embedding]
    except (TypeError, ValueError) as exc:
        raise _invalid_vector_dimension() from exc
    if not all(math.isfinite(value) for value in vector):
        raise _invalid_vector_dimension()
    return vector


def _multimodal_http_error_code(status_code: int) -> str:
    if status_code >= 500:
        return "MULTIMODAL_EMBEDDING_HTTP_5XX"
    return _MULTIMODAL_HTTP_ERROR_CODES.get(
        status_code,
        f"MULTIMODAL_EMBEDDING_HTTP_{status_code}",
    )


def _invalid_embedding_response() -> EmbeddingProviderError:
    return EmbeddingProviderError(
        "多模态 Embedding 返回结构无效。",
        code="EMBEDDING_RESPONSE_INVALID",
    )


def _invalid_vector_dimension() -> EmbeddingProviderError:
    return EmbeddingProviderError(
        "Embedding 向量维度或数值无效。",
        code="EMBEDDING_VECTOR_DIMENSION_INVALID",
    )
