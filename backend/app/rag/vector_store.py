"""Vector-store Protocol only; no ChromaDB or local vector index is created."""

from collections.abc import Sequence
from typing import Protocol

from app.rag.schemas import KnowledgeChunk, RetrievalHit, RetrievalQuery


class VectorStore(Protocol):
    def upsert(self, chunks: Sequence[KnowledgeChunk]) -> int: ...

    def search(self, query: RetrievalQuery) -> Sequence[RetrievalHit]: ...

    def delete_by_source(self, source_id: str) -> int: ...

    def health(self) -> dict[str, str]: ...
