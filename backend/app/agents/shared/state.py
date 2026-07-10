"""Agent state independent from LangGraph or persistence technology."""

from pydantic import BaseModel, Field

from app.agents.shared.contracts import (
    AgentErrorInfo,
    AgentEvent,
    AgentRunStatus,
    KnowledgeSourceReference,
)


class AgentState(BaseModel):
    run_id: str
    trace_id: str
    actor_user_id: int
    status: AgentRunStatus = AgentRunStatus.PENDING
    current_agent: str | None = None
    current_node: str | None = None
    current_candidate_id: int | None = None
    events: list[AgentEvent] = Field(default_factory=list)
    sources: list[KnowledgeSourceReference] = Field(default_factory=list)
    error: AgentErrorInfo | None = None

