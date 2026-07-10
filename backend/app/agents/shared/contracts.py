"""Shared, auditable contracts for Agent runs and events."""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AgentNodeStatus(str, Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class AgentEventType(str, Enum):
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    PLAN_CREATED = "PLAN_CREATED"
    AGENT_STARTED = "AGENT_STARTED"
    AGENT_THINKING = "AGENT_THINKING"
    TOOL_STARTED = "TOOL_STARTED"
    TOOL_COMPLETED = "TOOL_COMPLETED"
    KNOWLEDGE_RETRIEVED = "KNOWLEDGE_RETRIEVED"
    INTERMEDIATE_RESULT = "INTERMEDIATE_RESULT"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    CANDIDATE_COMPLETED = "CANDIDATE_COMPLETED"
    REVIEW_COMPLETED = "REVIEW_COMPLETED"
    REPORT_GENERATED = "REPORT_GENERATED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"


class AgentErrorInfo(BaseModel):
    code: str
    message: str
    retriable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class KnowledgeSourceReference(BaseModel):
    source_id: str
    title: str
    document_type: str | None = None
    department: str | None = None
    job_code: str | None = None
    version: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    effective_date: date | None = None
    excerpt: str | None = None
    relevance: float | None = Field(default=None, ge=0, le=1)


class AgentEvent(BaseModel):
    """Public event data. ``summary`` never contains hidden chain-of-thought."""

    event_id: str
    run_id: str
    trace_id: str
    candidate_id: int | None = None
    agent_name: str | None = None
    node_name: str | None = None
    display_name: str
    event_type: AgentEventType
    status: AgentNodeStatus
    summary: dict[str, Any] = Field(default_factory=dict)
    tool_name: str | None = None
    source_count: int = Field(default=0, ge=0)
    duration_ms: int | None = Field(default=None, ge=0)
    fallback_used: bool = False
    created_at: datetime
    error: AgentErrorInfo | None = None


class AgentNodeContract(BaseModel):
    name: str
    display_name: str
    responsibility: str
    required_inputs: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    allowed_tools: tuple[str, ...] = ()
    output_fields: tuple[str, ...] = ()
    forbidden_behaviors: tuple[str, ...] = ()
    can_skip: bool = False


class ToolContract(BaseModel):
    name: str
    description: str
    service_boundary: str
    permission: str
    read_only: bool
    sensitive: bool
    input_fields: tuple[str, ...] = ()
    output_fields: tuple[str, ...] = ()


class AgentRunSnapshot(BaseModel):
    run_id: str
    trace_id: str
    status: AgentRunStatus
    current_agent: str | None = None
    current_node: str | None = None
    completed_candidates: int = Field(default=0, ge=0)
    total_candidates: int = Field(default=0, ge=0)
    nodes: dict[str, AgentNodeStatus] = Field(default_factory=dict)
    events: list[AgentEvent] = Field(default_factory=list)
    sources: list[KnowledgeSourceReference] = Field(default_factory=list)
    error: AgentErrorInfo | None = None
    created_at: datetime
    updated_at: datetime

