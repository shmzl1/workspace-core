"""Future metadata, keyword, semantic and hybrid retrieval interfaces."""

from collections.abc import Sequence
from enum import Enum
from typing import Protocol

from app.rag.citations import Citation
from app.rag.schemas import KnowledgeChunk, RetrievalHit, RetrievalQuery, RetrievalResult


class RetrievalMode(str, Enum):
    METADATA = "METADATA"
    KEYWORD = "KEYWORD"
    SEMANTIC = "SEMANTIC"
    HYBRID = "HYBRID"


class KnowledgeRetriever(Protocol):
    def metadata_filter(self, query: RetrievalQuery) -> Sequence[KnowledgeChunk]: ...

    def keyword_search(self, query: RetrievalQuery) -> Sequence[RetrievalHit]: ...

    def semantic_search(self, query: RetrievalQuery) -> Sequence[RetrievalHit]: ...

    def hybrid_rank(self, query: RetrievalQuery, hits: Sequence[RetrievalHit]) -> RetrievalResult: ...

    def sources(self, result: RetrievalResult) -> Sequence[Citation]: ...
