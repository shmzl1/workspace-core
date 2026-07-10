"""Static contract for the not-yet-implemented job match node."""

from app.agents.shared import AgentNodeContract

JOB_MATCH_NODE = AgentNodeContract(
    name="job_match",
    display_name="岗位匹配 Agent",
    responsibility="依据候选人画像和岗位标准调用确定性评分 Service。",
    required_inputs=("candidate_profiles", "job_rubric"),
    dependencies=("resume_parser",),
    output_fields=("job_match_summaries",),
    forbidden_behaviors=("随机评分", "直接调用 human_only"),
)

