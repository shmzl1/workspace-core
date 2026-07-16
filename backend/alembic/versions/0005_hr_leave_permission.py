"""Grant HR specialists permission to read their own leave account.

Revision ID: 0005_hr_leave_permission
Revises: 0004_agent_runtime
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0005_hr_leave_permission"
down_revision: str | None = "0004_agent_runtime"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE users
            SET permissions = permissions || '["leave.self.read"]'::jsonb
            WHERE role = 'HR_SPECIALIST'
              AND NOT permissions @> '["leave.self.read"]'::jsonb
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE users
            SET permissions = permissions - 'leave.self.read'
            WHERE role = 'HR_SPECIALIST'
              AND permissions @> '["leave.self.read"]'::jsonb
            """
        )
    )
