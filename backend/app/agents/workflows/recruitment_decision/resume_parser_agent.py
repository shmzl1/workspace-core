"""Static contract for the not-yet-implemented resume parser node."""

from app.agents.shared import AgentNodeContract

RESUME_PARSER_NODE = AgentNodeContract(
    name="resume_parser",
    display_name="简历解析 Agent",
    responsibility="提取候选人事实和证据。",
    required_inputs=("execution_plan", "candidate_ids"),
    dependencies=("recruitment_strategy",),
    output_fields=("candidate_profiles",),
    forbidden_behaviors=("伪造简历事实", "输出完整简历到事件"),
)

