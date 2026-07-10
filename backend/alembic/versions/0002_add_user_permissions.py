"""Add persistent user permissions and backfill role defaults.

Revision ID: 0002_add_user_permissions
Revises: 0001_initial_schema
"""

from __future__ import annotations

import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_add_user_permissions"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


ROLE_DEFAULT_PERMISSIONS = {
    "EMPLOYEE": ["employee.self.read", "attendance.self.read", "attendance.self.manage", "leave.self.read", "payroll.self.read", "policy.read", "agent.employee.use"],
    "DEPARTMENT_MANAGER": ["employee.self.read", "employee.department.read", "attendance.self.read", "attendance.self.manage", "leave.self.read", "payroll.self.read", "payroll.department.read", "interview.read", "policy.read", "agent.employee.use"],
    "HR_SPECIALIST": ["employee.self.read", "recruitment.read", "recruitment.manage", "candidate.read", "candidate.score", "candidate.stage.manage", "interview.read", "interview.manage", "reporting.recruitment.read", "payroll.masked.read", "policy.read", "audit.read", "agent.hr.use"],
    "PAYROLL_ADMIN": ["employee.self.read", "payroll.self.read", "payroll.all.read", "payroll.review.read", "payroll.review.manage", "audit.read", "policy.read"],
}


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "permissions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    for role, permissions in ROLE_DEFAULT_PERMISSIONS.items():
        op.execute(
            sa.text("UPDATE users SET permissions = CAST(:permissions AS jsonb) WHERE role = :role").bindparams(
                permissions=json.dumps(permissions, ensure_ascii=True),
                role=role,
            )
        )


def downgrade() -> None:
    op.drop_column("users", "permissions")
