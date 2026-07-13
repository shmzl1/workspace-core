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
    EmbeddingProviderError,
    KnowledgeBaseConfigurationError,
    KnowledgeBaseDisabledError,
    KnowledgeBaseError,
    KnowledgeBaseUnavailableError,
    KnowledgeMappingError,
    KnowledgeDocumentError,
)
from app.rag.lifecycle import (
    ChromaKnowledgeBaseLifecycle,
    DisabledKnowledgeBaseLifecycle,
    KnowledgeBaseLifecycle,
    NotImplementedKnowledgeBaseLifecycle,
)
from app.rag.retrieval.gateway import (
    ChromaRetrievalGateway,
    DisabledRetrievalGateway,
    NotImplementedRetrievalGateway,
    RetrievalGateway,
)
from app.rag.status import KnowledgeBaseRuntimeState, KnowledgeBaseStatus
from app.rag.embedding import (
    EmbeddingClient,
    OpenAICompatibleEmbeddingClient,
    VolcengineMultimodalEmbeddingClient,
    parse_volcengine_multimodal_embedding_response,
)
from app.rag.vector_store import ChromaVectorStore

__all__ = [
    "ChromaKnowledgeBaseLifecycle",
    "ChromaRetrievalGateway",
    "ChromaVectorStore",
    "DisabledKnowledgeBaseLifecycle",
    "DisabledRetrievalGateway",
    "EmbeddingProviderError",
    "EmbeddingClient",
    "KnowledgeChunk",
    "KnowledgeBaseConfigurationError",
    "KnowledgeBaseDisabledError",
    "KnowledgeBaseError",
    "KnowledgeBaseLifecycle",
    "KnowledgeBaseRuntimeState",
    "KnowledgeBaseStatus",
    "KnowledgeBaseUnavailableError",
    "KnowledgeDocumentError",
    "KnowledgeMappingError",
    "NotImplementedKnowledgeBaseLifecycle",
    "NotImplementedRetrievalGateway",
    "OpenAICompatibleEmbeddingClient",
    "VolcengineMultimodalEmbeddingClient",
    "parse_volcengine_multimodal_embedding_response",
    "PolicyDocumentMetadata",
    "RetrievalFilter",
    "RetrievalGateway",
    "RetrievalHit",
    "RetrievalQuery",
    "RetrievalResult",
]
