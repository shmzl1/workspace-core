"""Static workflow metadata; no LangGraph object is created."""

from app.agents.shared import AgentNodeContract
from app.agents.workflows.recruitment_decision.decision_review_agent import DECISION_REVIEW_NODE
from app.agents.workflows.recruitment_decision.interview_evaluation_agent import INTERVIEW_EVALUATION_NODE
from app.agents.workflows.recruitment_decision.job_match_agent import JOB_MATCH_NODE
from app.agents.workflows.recruitment_decision.report_agent import HR_REPORT_NODE
from app.agents.workflows.recruitment_decision.resume_parser_agent import RESUME_PARSER_NODE
from app.agents.workflows.recruitment_decision.strategy_agent import RECRUITMENT_STRATEGY_NODE

RECRUITMENT_WORKFLOW_NODES: tuple[AgentNodeContract, ...] = (
    RECRUITMENT_STRATEGY_NODE,
    RESUME_PARSER_NODE,
    JOB_MATCH_NODE,
    INTERVIEW_EVALUATION_NODE,
    DECISION_REVIEW_NODE,
    HR_REPORT_NODE,
)

RECRUITMENT_WORKFLOW_EDGES: tuple[tuple[str, str], ...] = (
    ("recruitment_strategy", "resume_parser"),
    ("resume_parser", "job_match"),
    ("recruitment_strategy", "interview_evaluation"),
    ("job_match", "decision_review"),
    ("interview_evaluation", "decision_review"),
    ("decision_review", "hr_report"),
)

