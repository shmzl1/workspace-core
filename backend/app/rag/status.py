"""Knowledge-base health contract."""

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
