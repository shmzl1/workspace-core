"""Pure data contracts for planned recruitment intelligence analysis."""

from pydantic import BaseModel, Field


class NormalizedSkill(BaseModel):
    raw_name: str
    normalized_name: str
    aliases: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)


class ResumeExtractionResult(BaseModel):
    candidate_id: int
    normalized_skills: list[NormalizedSkill] = Field(default_factory=list)
    facts: dict[str, object] = Field(default_factory=dict)
    evidence_ids: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class EvidenceValidationResult(BaseModel):
    evidence_id: str
    valid: bool | None = None
    reason: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class JobRubricDefinition(BaseModel):
    job_id: int
    version: str | None = None
    required_items: list[dict[str, object]] = Field(default_factory=list)
    weighted_items: list[dict[str, object]] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)


class ConfidenceBreakdown(BaseModel):
    overall: float | None = Field(default=None, ge=0, le=100)
    evidence_coverage: float | None = Field(default=None, ge=0, le=100)
    profile_completeness: float | None = Field(default=None, ge=0, le=100)
    rubric_coverage: float | None = Field(default=None, ge=0, le=100)
    knowledge_relevance: float | None = Field(default=None, ge=0, le=100)
    agent_consistency: float | None = Field(default=None, ge=0, le=100)
    reduction_reasons: list[str] = Field(default_factory=list)
