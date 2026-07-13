"""High-level asynchronous retrieval gateway without a concrete vector store."""

from typing import Protocol

from app.rag.errors import (
    KnowledgeBaseConfigurationError,
    KnowledgeBaseDisabledError,
    KnowledgeBaseUnavailableError,
)
from app.rag.schemas import RetrievalQuery, RetrievalResult
from app.rag.status import KnowledgeBaseStatus


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
