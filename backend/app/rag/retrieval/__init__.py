"""Stable retrieval contracts; importing this package performs no retrieval."""

from app.rag.retrieval.contracts import KnowledgeRetriever, RetrievalMode
from app.rag.retrieval.gateway import (
    DisabledRetrievalGateway,
    NotImplementedRetrievalGateway,
    RetrievalGateway,
)

__all__ = [
    "DisabledRetrievalGateway",
    "KnowledgeRetriever",
    "NotImplementedRetrievalGateway",
    "RetrievalGateway",
    "RetrievalMode",
]
