"""Future document loading, splitting and indexing contracts."""

from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel, Field

from app.rag.schemas import KnowledgeChunk, PolicyDocumentMetadata


class LoadedKnowledgeDocument(BaseModel):
    metadata: PolicyDocumentMetadata
    content: str


class IngestionResult(BaseModel):
    source_id: str
    chunk_count: int = Field(ge=0)
    warnings: list[str] = Field(default_factory=list)


class KnowledgeLoader(Protocol):
    def load(self, source_path: str, metadata: PolicyDocumentMetadata) -> LoadedKnowledgeDocument: ...


class KnowledgeSplitter(Protocol):
    def split(self, document: LoadedKnowledgeDocument) -> Sequence[KnowledgeChunk]: ...


class KnowledgeIndexer(Protocol):
    def index(self, chunks: Sequence[KnowledgeChunk]) -> IngestionResult: ...
