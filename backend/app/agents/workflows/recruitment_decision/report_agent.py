"""HR-report node metadata and pure Tool orchestration."""

from app.agents.shared import AgentNodeContract
from app.agents.tools.recruitment_tools import RecruitmentReportTool
from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewSummary,
    EnterpriseKnowledgeSummary,
    HRReportSummary,
    InterviewEvaluationSummary,
    JobMatchSummary,
    RecruitmentGoal,
)

HR_REPORT_NODE = AgentNodeContract(
    name="hr_report",
    display_name="HR 最终报告",
    responsibility="汇总企业招聘目标、候选人证据、来源、审查结果和建议动作。",
    required_inputs=(
        "goal",
        "job_matches",
        "decision_reviews",
        "knowledge_summary",
        "candidate_profiles",
        "interview_evaluations",
    ),
    dependencies=("decision_review",),
    allowed_tools=("build_recruitment_report",),
    output_fields=("report",),
    forbidden_behaviors=("把建议表述为已录用决定", "确认薪资", "伪造来源"),
)


def build_hr_report(
    goal: RecruitmentGoal,
    job_matches: dict[int, JobMatchSummary],
    decision_reviews: dict[int, DecisionReviewSummary],
    knowledge: EnterpriseKnowledgeSummary,
    candidate_profiles: dict[int, CandidateProfile],
    interview_evaluations: dict[int, InterviewEvaluationSummary],
    tool: RecruitmentReportTool,
) -> HRReportSummary:
    """Invoke the injected report Tool without composing candidate results here."""

    return tool.invoke(
        goal,
        job_matches,
        decision_reviews,
        knowledge,
        candidate_profiles,
        interview_evaluations,
    )

