"""Safe knowledge-base integration errors."""


class KnowledgeBaseError(RuntimeError):
    """Base error for knowledge-base boundaries."""


class KnowledgeBaseDisabledError(KnowledgeBaseError):
    """Raised when disabled retrieval or lifecycle code is invoked."""


class KnowledgeBaseConfigurationError(KnowledgeBaseError):
    """Raised when enabled knowledge-base configuration is incomplete."""


class KnowledgeBaseUnavailableError(KnowledgeBaseError):
    """Raised when the real knowledge-base implementation is unavailable."""


class KnowledgeMappingError(KnowledgeBaseError):
    """Raised when retrieved knowledge cannot satisfy a domain contract."""


class KnowledgeDocumentError(KnowledgeBaseError):
    """Raised when a configured knowledge document cannot be loaded safely."""


class EmbeddingProviderError(KnowledgeBaseError):
    """Raised when the configured Embedding provider is unavailable or invalid."""
