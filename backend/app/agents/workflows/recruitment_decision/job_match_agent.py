"""Job-match node metadata and pure Tool orchestration."""

from app.agents.shared import AgentNodeContract
from app.agents.tools.recruitment_tools import CandidateEvaluationTool
from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    EnterpriseKnowledgeSummary,
    JobMatchSummary,
    JobRubric,
    RecruitmentRunContext,
)

JOB_MATCH_NODE = AgentNodeContract(
    name="job_match",
    display_name="岗位匹配 Agent",
    responsibility="依据候选人画像和岗位标准调用专业 Service，汇总确定性评分与技能缺口。",
    required_inputs=("context", "candidate_profiles", "job_rubric", "knowledge_summary"),
    dependencies=("resume_parser",),
    allowed_tools=("evaluate_candidate",),
    output_fields=("job_matches",),
    forbidden_behaviors=("自行编造确定性评分", "绕过必备条件", "直接调用 human_only"),
)


def run_job_match(
    context: RecruitmentRunContext,
    profile: CandidateProfile,
    rubric: JobRubric,
    knowledge: EnterpriseKnowledgeSummary,
    tool: CandidateEvaluationTool,
) -> JobMatchSummary:
    """Invoke the injected Tool without scoring or event publication here."""

    return tool.invoke(context, profile, rubric, knowledge)

