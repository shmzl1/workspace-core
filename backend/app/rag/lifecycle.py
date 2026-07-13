"""Knowledge-base lifecycle contracts and ChromaDB initialization."""

import asyncio
from pathlib import Path
from typing import Protocol

from app.rag.embedding import EmbeddingClient
from app.rag.errors import (
    EmbeddingProviderError,
    KnowledgeBaseConfigurationError,
    KnowledgeBaseDisabledError,
    KnowledgeBaseError,
)
from app.rag.ingestion.loader import LocalKnowledgeLoader, discover_manifests
from app.rag.ingestion.splitter import StructuredKnowledgeSplitter
from app.rag.status import KnowledgeBaseRuntimeState, KnowledgeBaseStatus
from app.rag.vector_store import ChromaVectorStore


class KnowledgeBaseLifecycle(Protocol):
    async def initialize(self) -> KnowledgeBaseStatus: ...

    async def get_status(self) -> KnowledgeBaseStatus: ...

    async def aclose(self) -> None: ...


class DisabledKnowledgeBaseLifecycle:
    def __init__(self, collection_name: str | None = None) -> None:
        self.collection_name = collection_name

    async def initialize(self) -> KnowledgeBaseStatus:
        raise KnowledgeBaseDisabledError("企业知识库当前已禁用。")

    async def get_status(self) -> KnowledgeBaseStatus:
        return KnowledgeBaseStatus(
            enabled=False, configured=False, ready=False, mode="DISABLED",
            collection_name=self.collection_name,
        )

    async def aclose(self) -> None:
        return None


class NotImplementedKnowledgeBaseLifecycle:
    def __init__(self, collection_name: str | None, *, configured: bool = True) -> None:
        self.collection_name = collection_name
        self.configured = configured

    async def initialize(self) -> KnowledgeBaseStatus:
        if not self.configured:
            raise KnowledgeBaseConfigurationError("企业知识库已启用，但配置不完整。")
        return await self.get_status()

    async def get_status(self) -> KnowledgeBaseStatus:
        return KnowledgeBaseStatus(
            enabled=True,
            configured=self.configured,
            ready=False,
            mode="NOT_IMPLEMENTED" if self.configured else "MISCONFIGURED",
            collection_name=self.collection_name,
        )

    async def aclose(self) -> None:
        return None


class ChromaKnowledgeBaseLifecycle:
    def __init__(
        self,
        *,
        policy_data_dir: str,
        loader: LocalKnowledgeLoader,
        splitter: StructuredKnowledgeSplitter,
        embedding_client: EmbeddingClient,
        vector_store: ChromaVectorStore,
        runtime_state: KnowledgeBaseRuntimeState,
    ) -> None:
        self.policy_data_dir = Path(policy_data_dir)
        self.loader = loader
        self.splitter = splitter
        self.embedding_client = embedding_client
        self.vector_store = vector_store
        self.runtime_state = runtime_state

    async def initialize(self) -> KnowledgeBaseStatus:
        self.runtime_state.set(ready=False, mode="DEGRADED", last_error="RAG_INITIALIZING")
        warnings: list[str] = []
        indexed_documents = 0
        try:
            await asyncio.to_thread(self.vector_store.open)
            discovery = await asyncio.to_thread(discover_manifests, self.policy_data_dir)
            warnings.extend(discovery.warnings)
            for source_path, entry in discovery.entries:
                if not entry.is_active:
                    await asyncio.to_thread(self.vector_store.delete_by_source, entry.source_id)
                    continue
                try:
                    document = await asyncio.to_thread(self.loader.load, str(source_path), entry)
                    chunks = list(self.splitter.split(document))
                    if not chunks:
                        warnings.append(f"DOCUMENT_NO_CHUNKS:{entry.source_id}")
                        continue
                    embeddings = await self.embedding_client.embed([chunk.text for chunk in chunks])
                    await asyncio.to_thread(self.vector_store.delete_by_source, entry.source_id)
                    await asyncio.to_thread(self.vector_store.upsert, chunks, embeddings)
                    indexed_documents += 1
                except EmbeddingProviderError as exc:
                    warnings.append(exc.code)
                except (KnowledgeBaseError, OSError, ValueError, TypeError):
                    warnings.append(f"DOCUMENT_INDEX_FAILED:{entry.source_id}")
            health = await asyncio.to_thread(self.vector_store.health)
            if indexed_documents == 0 or not health.get("chunk_count"):
                return self.runtime_state.set(
                    ready=False,
                    mode="DEGRADED",
                    document_count=health.get("document_count"),
                    chunk_count=health.get("chunk_count"),
                    last_error=warnings[0] if warnings else "NO_INDEXED_DOCUMENTS",
                )
            return self.runtime_state.set(
                ready=True,
                mode="DEGRADED" if warnings else "READY",
                document_count=health.get("document_count"),
                chunk_count=health.get("chunk_count"),
                last_error=warnings[0] if warnings else None,
            )
        except Exception:
            return self.runtime_state.set(
                ready=False,
                mode="DEGRADED",
                document_count=None,
                chunk_count=None,
                last_error="RAG_INITIALIZATION_FAILED",
            )

    async def get_status(self) -> KnowledgeBaseStatus:
        return self.runtime_state.get()

    async def aclose(self) -> None:
        await self.embedding_client.aclose()
        await asyncio.to_thread(self.vector_store.aclose)
