"""Contracts for the Sprint 2 recruitment decision workflow."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.agents.shared import (
    AgentNodeStatus,
    AgentRunSnapshot,
    AgentState,
    KnowledgeSourceReference,
)


class RecruitmentUrgency(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecruitmentGoal(BaseModel):
    job_id: int
    job_title: str = ""
    department: str = ""
    target_headcount: int = Field(ge=1)
    deadline: date | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_experience_months: int = Field(default=0, ge=0)
    score_threshold: float = Field(default=0, ge=0, le=100)
    confidence_threshold: float = Field(default=0, ge=0, le=100)
    urgency: RecruitmentUrgency = RecruitmentUrgency.NORMAL
    optional_salary_budget: float | None = Field(default=None, ge=0)


class RecruitmentRunRequest(BaseModel):
    goal: RecruitmentGoal
    candidate_ids: list[int] = Field(default_factory=list)


class RecruitmentJobContext(BaseModel):
    job_id: int
    job_code: str
    job_title: str
    department: str
    status: str
    description: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_experience_months: int = Field(default=0, ge=0)
    source_version: str
    effective_date: date


class RecruitmentCandidateContext(BaseModel):
    candidate_id: int
    application_id: int
    skills: list[str] = Field(default_factory=list)
    experience_months: int | None = Field(default=None, ge=0)
    availability: str | None = None
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    project_roles: list[str] = Field(default_factory=list)
    project_technologies: list[str] = Field(default_factory=list)
    measurable_achievements: list[str] = Field(default_factory=list)
    certificates: list[str] = Field(default_factory=list)
    resume_excerpt: str | None = Field(default=None, max_length=1500)


class RecruitmentRunContext(BaseModel):
    request: RecruitmentRunRequest
    job: RecruitmentJobContext
    candidate_ids: list[int] = Field(default_factory=list)
    application_ids: list[int] = Field(default_factory=list)
    candidates: list[RecruitmentCandidateContext] = Field(default_factory=list)
    interview_candidate_ids: list[int] = Field(default_factory=list)


class RecruitmentExecutionPlan(BaseModel):
    goal: RecruitmentGoal
    candidate_ids: list[int] = Field(default_factory=list)
    candidate_count: int = Field(ge=0)
    required_nodes: list[str] = Field(default_factory=list)
    executed_nodes: list[str] = Field(default_factory=list)
    skipped_nodes: list[str] = Field(default_factory=list)
    resume_parse_required: bool = True
    interview_candidate_ids: list[int] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    interview_evaluation_requires_real_data: bool = True
    current_phase: str = "SPRINT_2_3_DETERMINISTIC_INTERMEDIATE"
    next_phase: str = "LLM_RAG_INTEGRATION"
    plan_notes: list[str] = Field(default_factory=list)


class RecruitmentRunSnapshot(AgentRunSnapshot):
    goal: RecruitmentGoal
    job: RecruitmentJobContext
    candidate_ids: list[int] = Field(default_factory=list)
    execution_plan: RecruitmentExecutionPlan | None = None
    candidate_profiles: dict[int, "CandidateProfile"] = Field(default_factory=dict)
    job_rubric: JobRubric | None = None
    knowledge_summary: EnterpriseKnowledgeSummary | None = None
    job_matches: dict[int, JobMatchSummary] = Field(default_factory=dict)
    interview_evaluations: dict[int, InterviewEvaluationSummary] = Field(default_factory=dict)
    decision_reviews: dict[int, DecisionReviewSummary] = Field(default_factory=dict)
    report: HRReportSummary | None = None


class ResumeEvidenceItem(BaseModel):
    evidence_id: str
    capability: str
    excerpt: str
    source_section: str | None = None
    supports: bool | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class CandidateProfile(BaseModel):
    candidate_id: int
    skills: list[str] = Field(default_factory=list)
    normalized_skills: list[str] = Field(default_factory=list)
    experience_months: int | None = Field(default=None, ge=0)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    project_roles: list[str] = Field(default_factory=list)
    project_technologies: list[str] = Field(default_factory=list)
    measurable_achievements: list[str] = Field(default_factory=list)
    certificates: list[str] = Field(default_factory=list)
    availability: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    evidence_items: list[ResumeEvidenceItem] = Field(default_factory=list)
    extraction_mode: str = "STRUCTURED_FALLBACK"
    fallback_used: bool = True


class JobRequirementItem(BaseModel):
    requirement_id: str
    category: str
    description: str
    required: bool
    weight: float | None = Field(default=None, ge=0)
    source_ids: list[str] = Field(default_factory=list)


class JobRubric(BaseModel):
    job_id: int
    version: str | None = None
    requirements: list[JobRequirementItem] = Field(default_factory=list)


class EnterpriseKnowledgeSummary(BaseModel):
    job_id: int
    job_code: str
    standard_version: str
    effective_date: date
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_experience_months: int = Field(default=0, ge=0)
    interview_criteria: list[str] = Field(default_factory=list)
    risk_rules: list[str] = Field(default_factory=list)
    retrieval_mode: str = "LOCAL_HYBRID_FALLBACK"
    sources: list[KnowledgeSourceReference] = Field(default_factory=list)


class JobMatchSummary(BaseModel):
    candidate_id: int
    overall_score: float | None = Field(default=None, ge=0, le=100)
    job_match_score: float | None = Field(default=None, ge=0, le=100)
    dimension_scores: dict[str, float] = Field(default_factory=dict)
    must_have_passed: bool | None = None
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    knowledge_sources: list[KnowledgeSourceReference] = Field(default_factory=list)
    suggested_interview_questions: list[str] = Field(default_factory=list)
    recommended_action: str | None = None
    scoring_mode: str = "DETERMINISTIC_HUMAN_ONLY"
    requires_review: bool = False


class InterviewEvaluationInput(BaseModel):
    candidate_id: int
    interview_id: int | None = None
    interview_status: str
    interviewer_scores: dict[str, float] = Field(default_factory=dict)
    structured_feedback: dict[str, Any] = Field(default_factory=dict)


class InterviewEvaluationSummary(BaseModel):
    candidate_id: int
    interview_id: int | None = None
    status: str
    conclusion: str
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    requires_review: bool = False


class DecisionReviewFinding(BaseModel):
    code: str
    severity: str
    summary: str
    evidence_ids: list[str] = Field(default_factory=list)
    requires_human_review: bool = False


class DecisionReviewSummary(BaseModel):
    candidate_id: int
    confidence: float | None = Field(default=None, ge=0, le=100)
    findings: list[DecisionReviewFinding] = Field(default_factory=list)
    risk_tags: list[str] = Field(default_factory=list)
    agent_disagreements: list[str] = Field(default_factory=list)
    deterministic_score_preserved: bool = True
    recommended_action: str | None = None
    review_mode: str = "RULE_BASED_INTERMEDIATE"


class HRReportSummary(BaseModel):
    goal: RecruitmentGoal
    candidate_rankings: list[int] = Field(default_factory=list)
    candidate_reviews: list[DecisionReviewSummary] = Field(default_factory=list)
    knowledge_sources: list[KnowledgeSourceReference] = Field(default_factory=list)
    talent_gaps: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    requires_human_decision: bool = True
    generation_mode: str = "RULE_BASED_INTERMEDIATE"


class RecruitmentDecisionState(AgentState):
    context: RecruitmentRunContext
    execution_plan: RecruitmentExecutionPlan | None = None
    candidate_profiles: dict[int, CandidateProfile] = Field(default_factory=dict)
    job_rubric: JobRubric | None = None
    knowledge_summary: EnterpriseKnowledgeSummary | None = None
    job_matches: dict[int, JobMatchSummary] = Field(default_factory=dict)
    interview_evaluations: dict[int, InterviewEvaluationSummary] = Field(default_factory=dict)
    decision_reviews: dict[int, DecisionReviewSummary] = Field(default_factory=dict)
    report: HRReportSummary | None = None
    node_statuses: dict[str, AgentNodeStatus] = Field(default_factory=dict)

