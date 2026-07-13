"""Stable ingestion contracts; importing this package performs no ingestion."""

from app.rag.ingestion.contracts import (
    IngestionResult,
    KnowledgeIndexer,
    KnowledgeLoader,
    KnowledgeSplitter,
    LoadedKnowledgeDocument,
)

__all__ = ["IngestionResult", "KnowledgeIndexer", "KnowledgeLoader", "KnowledgeSplitter", "LoadedKnowledgeDocument"]
