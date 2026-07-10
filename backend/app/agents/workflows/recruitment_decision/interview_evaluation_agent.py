"""Static contract for the not-yet-implemented interview evaluation node."""

from app.agents.shared import AgentNodeContract

INTERVIEW_EVALUATION_NODE = AgentNodeContract(
    name="interview_evaluation",
    display_name="面试评估 Agent",
    responsibility="只根据真实结构化面试数据生成评价。",
    required_inputs=("interview_data",),
    dependencies=("recruitment_strategy",),
    output_fields=("interview_evaluations",),
    forbidden_behaviors=("伪造面试结果", "自动确认排期"),
    can_skip=True,
)

