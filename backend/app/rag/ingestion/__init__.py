"""Stable ingestion contracts; importing this package performs no ingestion."""

from app.rag.ingestion.contracts import (
    IngestionResult,
    KnowledgeIndexer,
    KnowledgeLoader,
    KnowledgeSplitter,
    LoadedKnowledgeDocument,
)
from app.rag.ingestion.loader import (
    LocalKnowledgeLoader,
    ManifestDiscoveryResult,
    ManifestEntry,
    discover_manifests,
)
from app.rag.ingestion.splitter import StructuredKnowledgeSplitter

__all__ = [
    "IngestionResult",
    "KnowledgeIndexer",
    "KnowledgeLoader",
    "KnowledgeSplitter",
    "LoadedKnowledgeDocument",
    "LocalKnowledgeLoader",
    "ManifestDiscoveryResult",
    "ManifestEntry",
    "StructuredKnowledgeSplitter",
    "discover_manifests",
]
