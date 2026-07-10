"""Static contract for the not-yet-implemented decision review node."""

from app.agents.shared import AgentNodeContract

DECISION_REVIEW_NODE = AgentNodeContract(
    name="decision_review",
    display_name="决策审查 Agent",
    responsibility="检查证据、冲突、来源和专业 Agent 分歧。",
    required_inputs=("job_match_summaries", "interview_evaluations"),
    dependencies=("job_match", "interview_evaluation"),
    output_fields=("decision_reviews",),
    forbidden_behaviors=("静默修改确定性评分", "自动录用或淘汰"),
)

