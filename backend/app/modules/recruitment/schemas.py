"""Recruitment schemas for Sprint 1 outer workflow."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_code: str
    title: str
    department: str
    required_skills: list[Any] = Field(default_factory=list)
    preferred_skills: list[Any] = Field(default_factory=list)
    min_experience_months: int
    status: str


class CandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_no: str
    full_name: str
    email: str | None = None
    skills: list[Any] = Field(default_factory=list)
    experience_months: int
    available_from: date | None = None
    source: str


class CandidateApplicationRead(BaseModel):
    id: int
    candidate_id: int
    candidate_name: str | None = None
    job_id: int
    job_title: str | None = None
    current_stage: str
    score_total: Decimal | None = None
    score_breakdown: dict[str, Any] = Field(default_factory=dict)
    weights_snapshot: dict[str, Any] = Field(default_factory=dict)
    scored_at: datetime | None = None


class RecruitmentDashboardRead(BaseModel):
    jobs_count: int
    candidates_count: int
    applications_count: int
    pending_score_count: int
    ready_message: str


class ScoreApplicationRequest(BaseModel):
    weights: dict[str, Decimal] = Field(default_factory=dict)
    note: str | None = None


class ScoreApplicationResponse(BaseModel):
    application_id: int
    status: str
    message: str
    score_total: Decimal | None = None
    score_breakdown: dict[str, Any] = Field(default_factory=dict)
    explanation: dict[str, Any] = Field(default_factory=dict)
    requires_human_only: bool = False
