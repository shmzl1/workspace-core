"""Recruitment schemas."""

import json

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_code: str
    title: str
    department: str
    required_skills: list[Any] = Field(default_factory=list)
    preferred_skills: list[Any] = Field(default_factory=list)
    min_experience_months: int
    description: str | None = None
    location: str | None = None
    employment_type: str
    status: str
    owner_user_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


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


class ParsedResumeCandidate(BaseModel):
    full_name: str = Field(min_length=1)
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_months: int = Field(default=0, ge=0)
    available_from: date | None = None
    target_job_title: str = Field(min_length=1)
    target_job_code: str | None = None
    target_department: str | None = None
    education: list[str] = Field(default_factory=list)
    work_experiences: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    project_roles: list[str] = Field(default_factory=list)
    project_technologies: list[str] = Field(default_factory=list)
    measurable_achievements: list[str] = Field(default_factory=list)
    certificates: list[str] = Field(default_factory=list)
    current_location: str | None = None
    summary: str | None = None

    @field_validator(
        "skills",
        "education",
        "work_experiences",
        "projects",
        "project_roles",
        "project_technologies",
        "measurable_achievements",
        "certificates",
        mode="before",
    )
    @classmethod
    def normalize_string_lists(cls, value: Any) -> list[str]:
        if value is None:
            return []
        items = value if isinstance(value, list) else [value]
        normalized: list[str] = []
        for item in items:
            if isinstance(item, str):
                text = item.strip()
            elif isinstance(item, (dict, list)):
                text = json.dumps(item, ensure_ascii=False, separators=(",", ":"))
            else:
                text = str(item).strip()
            if text:
                normalized.append(text)
        return normalized


class CandidateResumeImportItemRead(BaseModel):
    filename: str
    status: Literal["IMPORTED", "DUPLICATE", "FAILED"]
    full_name: str | None = None
    matched_job_id: int | None = None
    matched_job_title: str | None = None
    candidate_id: int | None = None
    application_id: int | None = None
    message: str


class CandidateResumeImportResponse(BaseModel):
    imported_count: int
    duplicate_count: int
    failed_count: int
    items: list[CandidateResumeImportItemRead]


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
    applied_at: datetime | None = None
    updated_at: datetime | None = None


class CandidatePipelineRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    from_stage: str | None = None
    to_stage: str
    note: str | None = None
    changed_by_user_id: int | None = None
    created_at: datetime


class CandidateApplicationDetailRead(BaseModel):
    application: CandidateApplicationRead
    candidate: CandidateRead
    job: JobRead
    pipeline_records: list[CandidatePipelineRecordRead] = Field(default_factory=list)


class AdvanceStageRequest(BaseModel):
    to_stage: str = Field(min_length=1, max_length=32)
    note: str | None = Field(default=None, max_length=2000)


class AdvanceStageResponse(BaseModel):
    application: CandidateApplicationRead
    pipeline_record: CandidatePipelineRecordRead


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
