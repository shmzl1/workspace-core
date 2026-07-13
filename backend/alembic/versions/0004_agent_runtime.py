"""Persist Agent Runs, nodes, events and Tool calls.

Revision ID: 0004_agent_runtime
Revises: 0003_add_leave_requests
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_agent_runtime"
down_revision: str | None = "0003_add_leave_requests"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


RUN_STATUSES = "'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'"
NODE_STATUSES = "'WAITING', 'RUNNING', 'COMPLETED', 'NEEDS_REVIEW', 'FAILED', 'SKIPPED'"
EVENT_TYPES = (
    "'WORKFLOW_STARTED', 'PLAN_CREATED', 'AGENT_STARTED', 'AGENT_THINKING', "
    "'TOOL_STARTED', 'TOOL_COMPLETED', 'KNOWLEDGE_RETRIEVED', 'INTERMEDIATE_RESULT', "
    "'AGENT_COMPLETED', 'CANDIDATE_COMPLETED', 'REVIEW_COMPLETED', 'REPORT_GENERATED', "
    "'WORKFLOW_COMPLETED', 'WORKFLOW_FAILED'"
)


def upgrade() -> None:
    op.create_table(
        "agent_runs",
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("workflow_type", sa.String(length=64), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_agent", sa.String(length=64), nullable=True),
        sa.Column("current_node", sa.String(length=64), nullable=True),
        sa.Column("current_candidate_id", sa.Integer(), nullable=True),
        sa.Column("terminal", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("state_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("error_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(f"status IN ({RUN_STATUSES})", name="ck_agent_runs_status"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_index("ix_agent_runs_owner_updated_at", "agent_runs", ["owner_user_id", "updated_at"])
    op.create_index("ix_agent_runs_status_updated_at", "agent_runs", ["status", "updated_at"])

    op.create_table(
        "agent_run_nodes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("node_name", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("attempt", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("input_summary_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("output_summary_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("error_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(f"status IN ({NODE_STATUSES})", name="ck_agent_run_nodes_status"),
        sa.ForeignKeyConstraint(["run_id"], ["agent_runs.run_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "node_name", "attempt", name="uq_agent_run_nodes_attempt"),
    )
    op.create_index("ix_agent_run_nodes_run_status", "agent_run_nodes", ["run_id", "status"])

    op.create_table(
        "agent_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=True),
        sa.Column("agent_name", sa.String(length=64), nullable=True),
        sa.Column("node_name", sa.String(length=64), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("summary_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("tool_name", sa.String(length=128), nullable=True),
        sa.Column("source_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("fallback_used", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("error_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(f"event_type IN ({EVENT_TYPES})", name="ck_agent_events_event_type"),
        sa.CheckConstraint(f"status IN ({NODE_STATUSES})", name="ck_agent_events_status"),
        sa.ForeignKeyConstraint(["run_id"], ["agent_runs.run_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", name="uq_agent_events_event_id"),
        sa.UniqueConstraint("run_id", "sequence_no", name="uq_agent_events_run_sequence"),
    )
    op.create_index("ix_agent_events_run_sequence", "agent_events", ["run_id", "sequence_no"])
    op.create_index("ix_agent_events_trace_id", "agent_events", ["trace_id"])

    op.create_table(
        "agent_tool_calls",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("started_event_id", sa.String(length=64), nullable=False),
        sa.Column("completed_event_id", sa.String(length=64), nullable=True),
        sa.Column("node_name", sa.String(length=64), nullable=True),
        sa.Column("tool_name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("input_summary_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("output_summary_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("error_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('RUNNING', 'COMPLETED', 'FAILED')", name="ck_agent_tool_calls_status"),
        sa.ForeignKeyConstraint(["run_id"], ["agent_runs.run_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["started_event_id"], ["agent_events.event_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["completed_event_id"], ["agent_events.event_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("started_event_id", name="uq_agent_tool_calls_started_event"),
    )
    op.create_index("ix_agent_tool_calls_run_created_at", "agent_tool_calls", ["run_id", "created_at"])
    op.create_index("ix_agent_tool_calls_run_tool", "agent_tool_calls", ["run_id", "tool_name"])


def downgrade() -> None:
    op.drop_index("ix_agent_tool_calls_run_tool", table_name="agent_tool_calls")
    op.drop_index("ix_agent_tool_calls_run_created_at", table_name="agent_tool_calls")
    op.drop_table("agent_tool_calls")
    op.drop_index("ix_agent_events_trace_id", table_name="agent_events")
    op.drop_index("ix_agent_events_run_sequence", table_name="agent_events")
    op.drop_table("agent_events")
    op.drop_index("ix_agent_run_nodes_run_status", table_name="agent_run_nodes")
    op.drop_table("agent_run_nodes")
    op.drop_index("ix_agent_runs_status_updated_at", table_name="agent_runs")
    op.drop_index("ix_agent_runs_owner_updated_at", table_name="agent_runs")
    op.drop_table("agent_runs")
