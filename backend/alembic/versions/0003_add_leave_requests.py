"""Persist leave request workflow and non-annual leave balances.

Revision ID: 0003_add_leave_requests
Revises: 0002_add_user_permissions
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0003_add_leave_requests"
down_revision: str | None = "0002_add_user_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_leave_balances_leave_type", "leave_balances", type_="check")
    op.create_check_constraint("ck_leave_balances_leave_type", "leave_balances", "leave_type IN ('ANNUAL', 'SICK', 'COMP_TIME')")
    op.create_table(
        "leave_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("leave_type", sa.String(length=32), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_hours", sa.Numeric(7, 2), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column("approved_by_user_id", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("leave_type IN ('ANNUAL', 'SICK', 'COMP_TIME')", name="ck_leave_requests_leave_type"),
        sa.CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')", name="ck_leave_requests_status"),
        sa.CheckConstraint("end_at > start_at", name="ck_leave_requests_time_range"),
        sa.CheckConstraint("duration_hours > 0", name="ck_leave_requests_duration_positive"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leave_requests_employee_start_at", "leave_requests", ["employee_id", "start_at"])
    op.create_index("ix_leave_requests_status", "leave_requests", ["status"])


def downgrade() -> None:
    op.drop_index("ix_leave_requests_status", table_name="leave_requests")
    op.drop_index("ix_leave_requests_employee_start_at", table_name="leave_requests")
    op.drop_table("leave_requests")
    op.drop_constraint("ck_leave_balances_leave_type", "leave_balances", type_="check")
    op.create_check_constraint("ck_leave_balances_leave_type", "leave_balances", "leave_type IN ('ANNUAL')")
