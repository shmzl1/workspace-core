"""Employee ORM models."""

from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class Employee(TimestampMixin, Base):
    """Employee profile linked to an optional user account."""

    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint(
            "employment_status IN ('ACTIVE', 'INACTIVE', 'ON_LEAVE')",
            name="ck_employees_employment_status",
        ),
        UniqueConstraint("user_id", name="uq_employees_user_id"),
        UniqueConstraint("employee_no", name="uq_employees_employee_no"),
        UniqueConstraint("email", name="uq_employees_email"),
        UniqueConstraint("phone", name="uq_employees_phone"),
        Index("ix_employees_department", "department"),
        Index("ix_employees_manager_employee_id", "manager_employee_id"),
        Index("ix_employees_employment_status", "employment_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    employee_no: Mapped[str] = mapped_column(String(32), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    manager_employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    hire_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    employment_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="ACTIVE",
        server_default=text("'ACTIVE'"),
    )


class LeaveBalance(TimestampMixin, Base):
    """Annual leave balance by employee and year."""

    __tablename__ = "leave_balances"
    __table_args__ = (
        CheckConstraint("leave_type IN ('ANNUAL', 'SICK', 'COMP_TIME')", name="ck_leave_balances_leave_type"),
        CheckConstraint("total_days >= 0", name="ck_leave_balances_total_days_nonnegative"),
        CheckConstraint("used_days >= 0", name="ck_leave_balances_used_days_nonnegative"),
        CheckConstraint("used_days <= total_days", name="ck_leave_balances_used_days_lte_total"),
        UniqueConstraint("employee_id", "year", "leave_type", name="uq_leave_balances_employee_year_type"),
        Index("ix_leave_balances_employee_year", "employee_id", "year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    leave_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="ANNUAL",
        server_default=text("'ANNUAL'"),
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    used_days: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0"),
        server_default=text("0"),
    )


class LeaveRequest(TimestampMixin, Base):
    """Employee leave request and approval record."""

    __tablename__ = "leave_requests"
    __table_args__ = (
        CheckConstraint("leave_type IN ('ANNUAL', 'SICK', 'COMP_TIME')", name="ck_leave_requests_leave_type"),
        CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')", name="ck_leave_requests_status"),
        CheckConstraint("end_at > start_at", name="ck_leave_requests_time_range"),
        CheckConstraint("duration_hours > 0", name="ck_leave_requests_duration_positive"),
        Index("ix_leave_requests_employee_start_at", "employee_id", "start_at"),
        Index("ix_leave_requests_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    leave_type: Mapped[str] = mapped_column(String(32), nullable=False)
    start_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(7, 2), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING", server_default=text("'PENDING'"))
    approved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
