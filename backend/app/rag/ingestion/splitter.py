"""Deterministic heading/paragraph-aware knowledge splitter."""

import hashlib
import re
from collections.abc import Sequence

from app.rag.ingestion.contracts import LoadedKnowledgeDocument
from app.rag.schemas import KnowledgeChunk


class StructuredKnowledgeSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("无效的知识分块配置。")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, document: LoadedKnowledgeDocument) -> Sequence[KnowledgeChunk]:
        content = document.content.replace("\r\n", "\n").replace("\r", "\n").strip()
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:20]
        pieces = self._paragraph_pieces(content)
        texts: list[str] = []
        current = ""
        for piece in pieces:
            if len(piece) > self.chunk_size:
                if current:
                    texts.append(current)
                    current = ""
                texts.extend(self._windows(piece))
                continue
            candidate = f"{current}\n\n{piece}".strip() if current else piece
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                texts.append(current)
                prefix = current[-self.chunk_overlap:] if self.chunk_overlap else ""
                overlapped = f"{prefix}\n\n{piece}".strip()
                current = overlapped if len(overlapped) <= self.chunk_size else piece
        if current:
            texts.append(current)
        return [
            KnowledgeChunk(
                chunk_id=f"{document.metadata.source_id}:{content_hash}:{ordinal}",
                source=document.metadata,
                text=text,
                ordinal=ordinal,
                attributes=document.attributes,
            )
            for ordinal, text in enumerate(texts)
            if text.strip()
        ]

    @staticmethod
    def _paragraph_pieces(content: str) -> list[str]:
        return [part.strip() for part in re.split(r"\n\s*\n|(?=^#{1,6}\s)", content, flags=re.MULTILINE) if part.strip()]

    def _windows(self, text: str) -> list[str]:
        stride = self.chunk_size - self.chunk_overlap
        return [text[start:start + self.chunk_size].strip() for start in range(0, len(text), stride) if text[start:start + self.chunk_size].strip()]
