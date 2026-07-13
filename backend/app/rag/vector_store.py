"""ChromaDB persistent vector store using caller-provided embeddings."""

import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from app.rag.errors import KnowledgeBaseUnavailableError
from app.rag.schemas import KnowledgeChunk, PolicyDocumentMetadata, RetrievalHit


class VectorStore(Protocol):
    def open(self) -> None: ...

    def upsert(self, chunks: Sequence[KnowledgeChunk], embeddings: Sequence[Sequence[float]]) -> int: ...

    def search(
        self,
        query_embedding: Sequence[float],
        *,
        where: dict[str, Any] | None,
        limit: int,
    ) -> Sequence[RetrievalHit]: ...

    def delete_by_source(self, source_id: str) -> int: ...

    def health(self) -> dict[str, int | str | bool | None]: ...

    def aclose(self) -> None: ...


class ChromaVectorStore:
    def __init__(self, persist_dir: str, collection_name: str) -> None:
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self._client: Any = None
        self._collection: Any = None

    def open(self) -> None:
        try:
            import chromadb

            self._client = chromadb.PersistentClient(path=str(self.persist_dir))
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise KnowledgeBaseUnavailableError("ChromaDB Collection 无法打开。") from exc

    def upsert(self, chunks: Sequence[KnowledgeChunk], embeddings: Sequence[Sequence[float]]) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunk 与 Embedding 数量不一致。")
        collection = self._require_collection()
        if not chunks:
            return 0
        try:
            collection.upsert(
                ids=[chunk.chunk_id for chunk in chunks],
                documents=[chunk.text for chunk in chunks],
                embeddings=[list(vector) for vector in embeddings],
                metadatas=[_metadata_for_chroma(chunk) for chunk in chunks],
            )
        except Exception as exc:
            raise KnowledgeBaseUnavailableError("ChromaDB 写入失败。") from exc
        return len(chunks)

    def search(
        self,
        query_embedding: Sequence[float],
        *,
        where: dict[str, Any] | None,
        limit: int,
    ) -> Sequence[RetrievalHit]:
        collection = self._require_collection()
        try:
            result = collection.query(
                query_embeddings=[list(query_embedding)],
                n_results=limit,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            raise KnowledgeBaseUnavailableError("ChromaDB 检索失败。") from exc
        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        hits: list[RetrievalHit] = []
        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances, strict=False):
            if not isinstance(metadata, dict) or not isinstance(document, str):
                continue
            hits.append(RetrievalHit(
                chunk=_chunk_from_chroma(str(chunk_id), document, metadata),
                relevance=_distance_to_relevance(distance),
                retrieval_method="CHROMA_SEMANTIC",
            ))
        return hits

    def delete_by_source(self, source_id: str) -> int:
        collection = self._require_collection()
        try:
            existing = collection.get(where={"source_id": source_id}, include=[])
            ids = existing.get("ids") or []
            if ids:
                collection.delete(ids=ids)
            return len(ids)
        except Exception as exc:
            raise KnowledgeBaseUnavailableError("ChromaDB 来源替换失败。") from exc

    def health(self) -> dict[str, int | str | bool | None]:
        if self._collection is None:
            return {
                "ready": False,
                "collection_name": self.collection_name,
                "document_count": None,
                "chunk_count": None,
            }
        try:
            chunk_count = int(self._collection.count())
            payload = self._collection.get(include=["metadatas"])
            source_ids = {
                metadata.get("source_id")
                for metadata in payload.get("metadatas") or []
                if isinstance(metadata, dict) and metadata.get("source_id")
            }
            return {
                "ready": True,
                "collection_name": self.collection_name,
                "document_count": len(source_ids),
                "chunk_count": chunk_count,
            }
        except Exception as exc:
            raise KnowledgeBaseUnavailableError("ChromaDB 状态读取失败。") from exc

    def aclose(self) -> None:
        self._collection = None
        self._client = None

    def _require_collection(self) -> Any:
        if self._collection is None:
            raise KnowledgeBaseUnavailableError("ChromaDB 尚未初始化。")
        return self._collection


def _metadata_for_chroma(chunk: KnowledgeChunk) -> dict[str, str | int | float | bool]:
    source = chunk.source
    metadata: dict[str, str | int | float | bool] = {
        "source_id": source.source_id,
        "title": source.title,
        "document_type": source.document_type,
        "is_active": source.is_active,
        "ordinal": chunk.ordinal,
        "attributes_json": json.dumps(chunk.attributes, ensure_ascii=False, separators=(",", ":")),
    }
    optional = {
        "department": source.department,
        "job_code": source.job_code,
        "version": source.version,
        "effective_from": source.effective_from.isoformat() if source.effective_from else None,
        "effective_to": source.effective_to.isoformat() if source.effective_to else None,
    }
    metadata.update({key: value for key, value in optional.items() if value is not None})
    return metadata


def _chunk_from_chroma(chunk_id: str, text: str, metadata: dict[str, Any]) -> KnowledgeChunk:
    attributes_raw = metadata.get("attributes_json", "{}")
    try:
        attributes = json.loads(attributes_raw) if isinstance(attributes_raw, str) else {}
    except json.JSONDecodeError:
        attributes = {}
    return KnowledgeChunk(
        chunk_id=chunk_id,
        source=PolicyDocumentMetadata(
            source_id=str(metadata.get("source_id", "")),
            title=str(metadata.get("title", "")),
            document_type=str(metadata.get("document_type", "")),
            department=_optional_text(metadata.get("department")),
            job_code=_optional_text(metadata.get("job_code")),
            version=_optional_text(metadata.get("version")),
            effective_from=_optional_date(metadata.get("effective_from")),
            effective_to=_optional_date(metadata.get("effective_to")),
            is_active=bool(metadata.get("is_active", True)),
        ),
        text=text,
        ordinal=int(metadata.get("ordinal", 0)),
        attributes=attributes if isinstance(attributes, dict) else {},
    )


def _distance_to_relevance(value: Any) -> float:
    try:
        distance = max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0
    return round(max(0.0, min(1.0, 1.0 - distance)), 6)


def _optional_text(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None


def _optional_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value)) if value else None
    except ValueError:
        return None
