"""Authentication ORM models."""

from sqlalchemy import Boolean, CheckConstraint, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class User(TimestampMixin, Base):
    """Application user account."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('EMPLOYEE', 'HR_SPECIALIST', 'DEPARTMENT_MANAGER', 'PAYROLL_ADMIN')",
            name="ck_users_role",
        ),
        UniqueConstraint("username", name="uq_users_username"),
        Index("ix_users_role", "role"),
        Index("ix_users_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    permissions: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
