"""Static contract for the not-yet-implemented decision review node."""

from app.agents.shared import AgentNodeContract

DECISION_REVIEW_NODE = AgentNodeContract(
    name="decision_review",
    display_name="决策审查 Agent",
    responsibility="检查证据、来源、必备条件、面试冲突和专业 Agent 分歧。",
    required_inputs=("job_matches", "interview_evaluations"),
    dependencies=("job_match", "interview_evaluation"),
    allowed_tools=("evidence_validation_service",),
    output_fields=("decision_reviews",),
    forbidden_behaviors=("静默篡改确定性评分", "自动录用或淘汰候选人"),
)

