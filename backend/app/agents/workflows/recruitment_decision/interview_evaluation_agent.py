"""Static contract for the not-yet-implemented interview evaluation node."""

from app.agents.shared import AgentNodeContract

INTERVIEW_EVALUATION_NODE = AgentNodeContract(
    name="interview_evaluation",
    display_name="面试评估 Agent",
    responsibility="仅在存在真实结构化面试数据时生成评价；否则标记待面试。",
    required_inputs=("execution_plan", "interview_data"),
    dependencies=("recruitment_strategy",),
    allowed_tools=("interview_read_service",),
    output_fields=("interview_evaluations",),
    forbidden_behaviors=("伪造面试数据", "自动确认面试排期", "替代 HR 做录用决定"),
    can_skip=True,
)

