"""RAG data contracts; no loader, embedding, index or retrieval is implemented."""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class PolicyDocumentMetadata(BaseModel):
    source_id: str
    title: str
    document_type: str
    department: str | None = None
    job_code: str | None = None
    version: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    is_active: bool = True


class KnowledgeChunk(BaseModel):
    chunk_id: str
    source: PolicyDocumentMetadata
    text: str
    ordinal: int = Field(ge=0)
    attributes: dict[str, Any] = Field(default_factory=dict)


class RetrievalFilter(BaseModel):
    document_types: list[str] = Field(default_factory=list)
    departments: list[str] = Field(default_factory=list)
    job_codes: list[str] = Field(default_factory=list)
    effective_on: date | None = None
    active_only: bool = True


class RetrievalQuery(BaseModel):
    text: str
    filters: RetrievalFilter = Field(default_factory=RetrievalFilter)
    limit: int = Field(default=10, ge=1, le=100)


class RetrievalHit(BaseModel):
    chunk: KnowledgeChunk
    relevance: float = Field(ge=0, le=1)
    retrieval_method: str


class RetrievalResult(BaseModel):
    query: RetrievalQuery
    hits: list[RetrievalHit] = Field(default_factory=list)
    mode: str
    warnings: list[str] = Field(default_factory=list)
