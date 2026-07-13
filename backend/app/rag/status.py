"""Knowledge-base health contract and shared runtime state."""

from pydantic import BaseModel


class KnowledgeBaseStatus(BaseModel):
    enabled: bool
    configured: bool
    ready: bool
    mode: str
    collection_name: str | None = None
    document_count: int | None = None
    chunk_count: int | None = None
    last_error: str | None = None


class KnowledgeBaseRuntimeState:
    def __init__(self, status: KnowledgeBaseStatus) -> None:
        self._status = status

    def get(self) -> KnowledgeBaseStatus:
        return self._status.model_copy(deep=True)

    def set(self, **changes: object) -> KnowledgeBaseStatus:
        self._status = self._status.model_copy(update=changes)
        return self.get()
