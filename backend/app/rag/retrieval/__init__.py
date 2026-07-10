"""Stable retrieval contracts; importing this package performs no retrieval."""

from app.rag.retrieval.contracts import KnowledgeRetriever, RetrievalMode

__all__ = ["KnowledgeRetriever", "RetrievalMode"]
