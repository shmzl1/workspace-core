"""Decision-review node metadata and pure Tool orchestration."""

from app.agents.shared import AgentNodeContract
from app.agents.tools.recruitment_tools import DecisionReviewTool
from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewSummary,
    InterviewEvaluationSummary,
    JobMatchSummary,
    RecruitmentGoal,
)

DECISION_REVIEW_NODE = AgentNodeContract(
    name="decision_review",
    display_name="决策审查 Agent",
    responsibility="检查证据、来源、必备条件、面试冲突和专业 Agent 分歧。",
    required_inputs=("goal", "candidate_profiles", "job_matches", "interview_evaluations"),
    dependencies=("job_match", "interview_evaluation"),
    allowed_tools=("review_candidate_decision",),
    output_fields=("decision_reviews",),
    forbidden_behaviors=("静默篡改确定性评分", "自动录用或淘汰候选人"),
)


def run_decision_review(
    goal: RecruitmentGoal,
    profile: CandidateProfile,
    job_match: JobMatchSummary,
    interview_evaluation: InterviewEvaluationSummary | None,
    tool: DecisionReviewTool,
) -> DecisionReviewSummary:
    """Invoke the injected review Tool without implementing review rules here."""

    return tool.invoke(goal, profile, job_match, interview_evaluation)

