"""Static contract for the not-yet-implemented HR report node."""

from app.agents.shared import AgentNodeContract

HR_REPORT_NODE = AgentNodeContract(
    name="hr_report",
    display_name="HR 最终报告",
    responsibility="汇总目标、证据、来源、审查和建议。",
    required_inputs=("decision_reviews",),
    dependencies=("decision_review",),
    output_fields=("hr_report",),
    forbidden_behaviors=("把建议写成已执行决定", "伪造来源"),
)

