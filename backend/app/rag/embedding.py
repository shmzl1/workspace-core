"""OpenAI-compatible Embedding client with bounded retries."""

import asyncio
from collections.abc import Sequence
from typing import Any

import httpx
from pydantic import SecretStr

from app.rag.errors import EmbeddingProviderError, KnowledgeBaseConfigurationError


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
