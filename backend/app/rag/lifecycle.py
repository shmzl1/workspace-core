"""Asynchronous knowledge-base lifecycle contracts without initialization side effects."""

from typing import Protocol

from app.rag.errors import KnowledgeBaseConfigurationError, KnowledgeBaseDisabledError
from app.rag.status import KnowledgeBaseStatus


class KnowledgeBaseLifecycle(Protocol):
    async def initialize(self) -> KnowledgeBaseStatus: ...

    async def get_status(self) -> KnowledgeBaseStatus: ...

    async def aclose(self) -> None: ...


class DisabledKnowledgeBaseLifecycle:
    def __init__(self, collection_name: str | None = None) -> None:
        self.collection_name = collection_name

    async def initialize(self) -> KnowledgeBaseStatus:
        raise KnowledgeBaseDisabledError("企业知识库当前已禁用。")

    async def get_status(self) -> KnowledgeBaseStatus:
        return KnowledgeBaseStatus(
            enabled=False, configured=False, ready=False, mode="DISABLED",
            collection_name=self.collection_name,
        )

    async def aclose(self) -> None:
        return None


class NotImplementedKnowledgeBaseLifecycle:
    def __init__(self, collection_name: str | None, *, configured: bool = True) -> None:
        self.collection_name = collection_name
        self.configured = configured

    async def initialize(self) -> KnowledgeBaseStatus:
        if not self.configured:
            raise KnowledgeBaseConfigurationError("企业知识库已启用，但配置不完整。")
        return await self.get_status()

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
