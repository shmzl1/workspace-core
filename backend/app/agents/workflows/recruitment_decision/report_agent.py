"""Static contract for the not-yet-implemented HR report node."""

from app.agents.shared import AgentNodeContract

HR_REPORT_NODE = AgentNodeContract(
    name="hr_report",
    display_name="HR 最终报告",
    responsibility="汇总企业招聘目标、候选人证据、来源、审查结果和建议动作。",
    required_inputs=("request.goal", "decision_reviews"),
    dependencies=("decision_review",),
    allowed_tools=("recruitment_report_service",),
    output_fields=("report",),
    forbidden_behaviors=("把建议表述为已录用决定", "确认薪资", "伪造来源"),
)

