"""Stable ingestion contracts; importing this package performs no ingestion."""

from app.rag.ingestion.contracts import IngestionResult, LoadedKnowledgeDocument

__all__ = ["IngestionResult", "LoadedKnowledgeDocument"]
