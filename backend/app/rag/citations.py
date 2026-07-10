"""Source-display contracts only; this module does not retrieve documents."""

from datetime import date
from typing import Protocol, Sequence

from pydantic import BaseModel, Field

from app.rag.schemas import RetrievalHit


class Citation(BaseModel):
    source_id: str
    title: str
    version: str | None = None
    effective_date: date | None = None
    excerpt: str
    relevance: float = Field(ge=0, le=1)


class CitationFormatter(Protocol):
    def format(self, hits: Sequence[RetrievalHit]) -> Sequence[Citation]: ...
