"""Stable RAG schemas; importing this package performs no indexing or retrieval."""

from app.rag.schemas import (
    KnowledgeChunk,
    PolicyDocumentMetadata,
    RetrievalFilter,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
)
from app.rag.errors import (
    KnowledgeBaseConfigurationError,
    KnowledgeBaseDisabledError,
    KnowledgeBaseError,
    KnowledgeBaseUnavailableError,
    KnowledgeMappingError,
)
from app.rag.lifecycle import (
    DisabledKnowledgeBaseLifecycle,
    KnowledgeBaseLifecycle,
    NotImplementedKnowledgeBaseLifecycle,
)
from app.rag.retrieval.gateway import (
    DisabledRetrievalGateway,
    NotImplementedRetrievalGateway,
    RetrievalGateway,
)
from app.rag.status import KnowledgeBaseStatus

__all__ = [
    "KnowledgeChunk",
    "PolicyDocumentMetadata",
    "RetrievalFilter",
    "RetrievalHit",
    "RetrievalQuery",
    "RetrievalResult",
    "DisabledKnowledgeBaseLifecycle",
    "DisabledRetrievalGateway",
    "KnowledgeBaseConfigurationError",
    "KnowledgeBaseDisabledError",
    "KnowledgeBaseError",
    "KnowledgeBaseLifecycle",
    "KnowledgeBaseStatus",
    "KnowledgeBaseUnavailableError",
    "KnowledgeMappingError",
    "NotImplementedKnowledgeBaseLifecycle",
    "NotImplementedRetrievalGateway",
    "RetrievalGateway",
]
