"""High-level asynchronous retrieval gateways."""

import re
from typing import Protocol

from app.rag.errors import (
    EmbeddingProviderError,
    KnowledgeBaseError,
    KnowledgeBaseConfigurationError,
    KnowledgeBaseDisabledError,
    KnowledgeBaseUnavailableError,
)
from app.rag.schemas import RetrievalQuery, RetrievalResult
from app.rag.status import KnowledgeBaseRuntimeState, KnowledgeBaseStatus
from app.rag.embedding import EmbeddingClient
from app.rag.vector_store import ChromaVectorStore


class RetrievalGateway(Protocol):
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult: ...

    async def get_status(self) -> KnowledgeBaseStatus: ...

    async def aclose(self) -> None: ...


class DisabledRetrievalGateway:
    def __init__(self, collection_name: str | None = None) -> None:
        self.collection_name = collection_name

    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        del query
        raise KnowledgeBaseDisabledError("企业知识库当前已禁用。")

    async def get_status(self) -> KnowledgeBaseStatus:
        return KnowledgeBaseStatus(
            enabled=False,
            configured=False,
            ready=False,
            mode="DISABLED",
            collection_name=self.collection_name,
        )

    async def aclose(self) -> None:
        return None


class NotImplementedRetrievalGateway:
    def __init__(self, collection_name: str | None, *, configured: bool = True) -> None:
        self.collection_name = collection_name
        self.configured = configured

    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        del query
        if not self.configured:
            raise KnowledgeBaseConfigurationError("企业知识库已启用，但配置不完整。")
        raise KnowledgeBaseUnavailableError("真实知识检索尚未实现。")

    async def get_status(self) -> KnowledgeBaseStatus:
        return KnowledgeBaseStatus(
            enabled=True,
            configured=self.configured,
            ready=False,
            mode="NOT_IMPLEMENTED" if self.configured else "MISCONFIGURED",
            collection_name=self.collection_name,
        )

    async def aclose(self) -> None:
        return None


class ChromaRetrievalGateway:
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        vector_store: ChromaVectorStore,
        runtime_state: KnowledgeBaseRuntimeState,
        *,
        top_k: int,
        score_threshold: float,
    ) -> None:
        self.embedding_client = embedding_client
        self.vector_store = vector_store
        self.runtime_state = runtime_state
        self.top_k = top_k
        self.score_threshold = score_threshold

    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        status = self.runtime_state.get()
        if not status.configured:
            raise KnowledgeBaseConfigurationError("企业知识库配置不完整。")
        if not status.ready:
            raise KnowledgeBaseUnavailableError("企业知识库尚未就绪。")
        try:
            vectors = await self.embedding_client.embed([query.text])
            semantic_hits = self.vector_store.search(
                vectors[0],
                where=_chroma_where(query),
                limit=max(query.limit, self.top_k) * 4,
            )
            filtered = [hit for hit in semantic_hits if _matches_filter(hit, query)]
            ranked = _hybrid_rank(query.text, filtered)
            selected = [hit for hit in ranked if hit.relevance >= self.score_threshold][
                : min(query.limit, self.top_k)
            ]
        except EmbeddingProviderError as exc:
            self.runtime_state.set(mode="DEGRADED", last_error=exc.code)
            raise
        except KnowledgeBaseError:
            self.runtime_state.set(mode="DEGRADED", last_error="RAG_RETRIEVAL_FAILED")
            raise
        except (TypeError, ValueError) as exc:
            self.runtime_state.set(mode="DEGRADED", last_error="RAG_RESULT_INVALID")
            raise KnowledgeBaseUnavailableError("知识检索结果无效。") from exc
        warnings = [] if selected else ["NO_MATCHING_CHROMA_HITS"]
        return RetrievalResult(
            query=query,
            hits=selected,
            mode="CHROMA_HYBRID",
            warnings=warnings,
            fallback_used=False,
            provider="chromadb",
        )

    async def get_status(self) -> KnowledgeBaseStatus:
        return self.runtime_state.get()

    async def aclose(self) -> None:
        await self.embedding_client.aclose()


def _chroma_where(query: RetrievalQuery) -> dict[str, object] | None:
    conditions: list[dict[str, object]] = []
    if query.filters.active_only:
        conditions.append({"is_active": True})
    if query.filters.document_types:
        conditions.append({"document_type": {"$in": query.filters.document_types}})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def _matches_filter(hit: object, query: RetrievalQuery) -> bool:
    chunk = getattr(hit, "chunk", None)
    source = getattr(chunk, "source", None)
    if source is None:
        return False
    filters = query.filters
    if filters.document_types and source.document_type not in filters.document_types:
        return False
    if filters.departments and source.department and source.department not in filters.departments:
        return False
    if filters.job_codes and source.job_code and source.job_code not in filters.job_codes:
        return False
    if filters.active_only and not source.is_active:
        return False
    if filters.effective_on:
        if source.effective_from and source.effective_from > filters.effective_on:
            return False
        if source.effective_to and source.effective_to < filters.effective_on:
            return False
    return True


def _hybrid_rank(query_text: str, hits: list[object]) -> list:
    query_tokens = _tokens(query_text)
    ranked = []
    for hit in hits:
        text_tokens = _tokens(hit.chunk.text)
        keyword_score = len(query_tokens & text_tokens) / max(1, len(query_tokens))
        relevance = round(min(1.0, hit.relevance * 0.8 + keyword_score * 0.2), 6)
        ranked.append(hit.model_copy(update={
            "relevance": relevance,
            "retrieval_method": "CHROMA_HYBRID",
        }))
    return sorted(ranked, key=lambda item: item.relevance, reverse=True)


def _tokens(value: str) -> set[str]:
    return {
        token.casefold()
        for token in re.findall(r"[A-Za-z0-9+#.]+|[\u4e00-\u9fff]{2,}", value)
        if token.strip()
    }
