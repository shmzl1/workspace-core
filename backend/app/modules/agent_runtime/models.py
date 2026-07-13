"""PostgreSQL models for auditable Agent Run persistence."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


RUN_STATUSES = "'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'"
NODE_STATUSES = "'WAITING', 'RUNNING', 'COMPLETED', 'NEEDS_REVIEW', 'FAILED', 'SKIPPED'"
EVENT_TYPES = (
    "'WORKFLOW_STARTED', 'PLAN_CREATED', 'AGENT_STARTED', 'AGENT_THINKING', "
    "'TOOL_STARTED', 'TOOL_COMPLETED', 'KNOWLEDGE_RETRIEVED', 'INTERMEDIATE_RESULT', "
    "'AGENT_COMPLETED', 'CANDIDATE_COMPLETED', 'REVIEW_COMPLETED', 'REPORT_GENERATED', "
    "'WORKFLOW_COMPLETED', 'WORKFLOW_FAILED'"
)


class AgentRun(Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        CheckConstraint(f"status IN ({RUN_STATUSES})", name="ck_agent_runs_status"),
        Index("ix_agent_runs_owner_updated_at", "owner_user_id", "updated_at"),
        Index("ix_agent_runs_status_updated_at", "status", "updated_at"),
    )

    run_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workflow_type: Mapped[str] = mapped_column(String(64), nullable=False)
    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    current_agent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    current_node: Mapped[str | None] = mapped_column(String(64), nullable=True)
    current_candidate_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    terminal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    state_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    error_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class AgentRunNode(Base):
    __tablename__ = "agent_run_nodes"
    __table_args__ = (
        CheckConstraint(f"status IN ({NODE_STATUSES})", name="ck_agent_run_nodes_status"),
        UniqueConstraint("run_id", "node_name", "attempt", name="uq_agent_run_nodes_attempt"),
        Index("ix_agent_run_nodes_run_status", "run_id", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        ForeignKey("agent_runs.run_id", ondelete="CASCADE"), nullable=False
    )
    node_name: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text("1"))
    input_summary_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    output_summary_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    error_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class AgentEventRecord(Base):
    __tablename__ = "agent_events"
    __table_args__ = (
        CheckConstraint(f"event_type IN ({EVENT_TYPES})", name="ck_agent_events_event_type"),
        CheckConstraint(f"status IN ({NODE_STATUSES})", name="ck_agent_events_status"),
        UniqueConstraint("event_id", name="uq_agent_events_event_id"),
        UniqueConstraint("run_id", "sequence_no", name="uq_agent_events_run_sequence"),
        Index("ix_agent_events_run_sequence", "run_id", "sequence_no"),
        Index("ix_agent_events_trace_id", "trace_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(64), nullable=False)
    run_id: Mapped[str] = mapped_column(
        ForeignKey("agent_runs.run_id", ondelete="CASCADE"), nullable=False
    )
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False)
    candidate_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    agent_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    node_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    summary_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    tool_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fallback_used: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    error_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AgentToolCall(Base):
    __tablename__ = "agent_tool_calls"
    __table_args__ = (
        CheckConstraint(
            "status IN ('RUNNING', 'COMPLETED', 'FAILED')",
            name="ck_agent_tool_calls_status",
        ),
        UniqueConstraint("started_event_id", name="uq_agent_tool_calls_started_event"),
        Index("ix_agent_tool_calls_run_created_at", "run_id", "created_at"),
        Index("ix_agent_tool_calls_run_tool", "run_id", "tool_name"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        ForeignKey("agent_runs.run_id", ondelete="CASCADE"), nullable=False
    )
    started_event_id: Mapped[str] = mapped_column(
        ForeignKey("agent_events.event_id", ondelete="CASCADE"), nullable=False
    )
    completed_event_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_events.event_id", ondelete="SET NULL"), nullable=True
    )
    node_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    input_summary_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    output_summary_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
