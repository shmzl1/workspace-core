"""Static contract for the not-yet-implemented job match node."""

from app.agents.shared import AgentNodeContract

JOB_MATCH_NODE = AgentNodeContract(
    name="job_match",
    display_name="岗位匹配 Agent",
    responsibility="依据候选人画像和岗位标准调用专业 Service，汇总确定性评分与技能缺口。",
    required_inputs=("candidate_profiles", "job_rubric"),
    dependencies=("resume_parser",),
    allowed_tools=("candidate_evaluation_service", "knowledge_retrieval"),
    output_fields=("job_matches",),
    forbidden_behaviors=("自行编造确定性评分", "绕过必备条件", "直接调用 human_only"),
)

