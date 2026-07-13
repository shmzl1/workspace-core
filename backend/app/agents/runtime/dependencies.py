"""Injected dependencies for the deterministic recruitment runner."""

from dataclasses import dataclass

from app.agents.shared import ModelGateway
from app.agents.tools.knowledge_tools import EnterpriseKnowledgeTool
from app.agents.tools.recruitment_tools import (
    CandidateEvaluationTool,
    CandidateProfileTool,
    DecisionReviewTool,
    RecruitmentReportTool,
)


@dataclass(frozen=True)
class RecruitmentRunnerDependencies:
    knowledge_tool: EnterpriseKnowledgeTool
    profile_tool: CandidateProfileTool
    candidate_evaluation_tool: CandidateEvaluationTool
    decision_review_tool: DecisionReviewTool
    report_tool: RecruitmentReportTool
    model_gateway: ModelGateway
