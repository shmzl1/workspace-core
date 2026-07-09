"""Recruitment schemas."""

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


class RecruitmentFunnelItem(BaseModel):
    label: str
    count: int
    rate: float


class RecruitmentDepartmentItem(BaseModel):
    department: str
    jobs_count: int
    applications_count: int
    hired_count: int
    completion_rate: float


class RecruitmentSourceItem(BaseModel):
    source: str
    count: int
    rate: float


class RecruitmentTrendItem(BaseModel):
    period: str
    applications_count: int
    hired_count: int
    average_score: float


class RecruitmentReportRead(BaseModel):
    time_range: str
    jobs_count: int
    open_jobs_count: int
    candidates_count: int
    applications_count: int
    scored_applications_count: int
    pending_score_count: int
    high_match_count: int
    interview_pending_count: int
    interviewing_count: int
    offered_count: int
    hired_count: int
    rejected_count: int
    average_score: float
    average_match_rate: float
    funnel: list[RecruitmentFunnelItem] = Field(default_factory=list)
    departments: list[RecruitmentDepartmentItem] = Field(default_factory=list)
    sources: list[RecruitmentSourceItem] = Field(default_factory=list)
    trends: list[RecruitmentTrendItem] = Field(default_factory=list)


class ScoreApplicationRequest(BaseModel):
    weights: dict[str, Decimal] = Field(default_factory=dict)
    note: str | None = None


class ScoreApplicationResponse(BaseModel):
    application_id: int
    status: str
    message: str
    score_total: Decimal | None = None
    overall_score: Decimal | None = None
    match_score: Decimal | None = None
    match_rate: Decimal | None = None
    skill_match: str | None = None
    experience_match: str | None = None
    education_match: str | None = None
    risk_tags: list[str] = Field(default_factory=list)
    risk_prompt: str | None = None
    recommended_action: str | None = None
    scoring_basis: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    score_breakdown: dict[str, Any] = Field(default_factory=dict)
    explanation: dict[str, Any] = Field(default_factory=dict)
    expected_module: str | None = None
    expected_function: str | None = None
    fallback_data: dict[str, Any] = Field(default_factory=dict)
    requires_human_only: bool = False
