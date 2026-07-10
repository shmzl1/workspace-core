"""Contracts for the Sprint 2.1 recruitment strategy run."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

from app.agents.shared import AgentNodeStatus, AgentRunSnapshot, AgentState


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


class RecruitmentRunContext(BaseModel):
    request: RecruitmentRunRequest
    job: RecruitmentJobContext
    candidate_ids: list[int] = Field(default_factory=list)
    application_ids: list[int] = Field(default_factory=list)


class RecruitmentExecutionPlan(BaseModel):
    goal: RecruitmentGoal
    candidate_ids: list[int] = Field(default_factory=list)
    candidate_count: int = Field(ge=0)
    required_nodes: list[str] = Field(default_factory=list)
    executed_nodes: list[str] = Field(default_factory=list)
    skipped_nodes: list[str] = Field(default_factory=list)
    interview_evaluation_requires_real_data: bool = True
    current_phase: str = "SPRINT_2_1_STRATEGY_ONLY"
    next_phase: str = "SPRINT_2_2"
    plan_notes: list[str] = Field(default_factory=list)


class RecruitmentRunSnapshot(AgentRunSnapshot):
    execution_plan: RecruitmentExecutionPlan | None = None


class RecruitmentDecisionState(AgentState):
    context: RecruitmentRunContext
    execution_plan: RecruitmentExecutionPlan | None = None
    node_statuses: dict[str, AgentNodeStatus] = Field(default_factory=dict)

