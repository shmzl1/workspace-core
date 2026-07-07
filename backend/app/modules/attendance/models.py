"""Attendance ORM models."""

from datetime import time

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, Time, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class WorkCalendar(TimestampMixin, Base):
    """Workday and holiday calendar."""

    __tablename__ = "work_calendars"
    __table_args__ = (
        CheckConstraint("late_grace_minutes >= 0", name="ck_work_calendars_late_grace_nonnegative"),
        Index("ix_work_calendars_is_workday", "is_workday"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    calendar_date: Mapped[Date] = mapped_column(Date, nullable=False, unique=True)
    is_workday: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    standard_check_in_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        default=time(9, 0),
        server_default=text("'09:00:00'"),
    )
    standard_check_out_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        default=time(18, 0),
        server_default=text("'18:00:00'"),
    )
    late_grace_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    holiday_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)


class AttendanceRecord(TimestampMixin, Base):
    """Daily attendance result for an employee."""

    __tablename__ = "attendance_records"
    __table_args__ = (
        CheckConstraint(
            "status IN ('NORMAL', 'LATE', 'EARLY_LEAVE', 'ABSENT', 'UNPAID_LEAVE', 'APPROVED_ANNUAL_LEAVE')",
            name="ck_attendance_records_status",
        ),
        CheckConstraint("source IN ('WEB', 'MINIPROGRAM', 'MANUAL', 'SEED')", name="ck_attendance_records_source"),
        CheckConstraint("late_minutes >= 0", name="ck_attendance_records_late_minutes_nonnegative"),
        CheckConstraint("early_leave_minutes >= 0", name="ck_attendance_records_early_leave_minutes_nonnegative"),
        CheckConstraint(
            "check_out_at IS NULL OR check_in_at IS NULL OR check_out_at > check_in_at",
            name="ck_attendance_records_checkout_after_checkin",
        ),
        UniqueConstraint("employee_id", "attendance_date", name="uq_attendance_records_employee_date"),
        Index("ix_attendance_records_employee_date", "employee_id", "attendance_date"),
        Index("ix_attendance_records_status", "status"),
        Index("ix_attendance_records_attendance_date", "attendance_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    attendance_date: Mapped[Date] = mapped_column(Date, nullable=False)
    check_in_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="NORMAL", server_default=text("'NORMAL'"))
    late_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    early_leave_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    leave_balance_id: Mapped[int | None] = mapped_column(
        ForeignKey("leave_balances.id", ondelete="SET NULL"),
        nullable=True,
    )
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="WEB", server_default=text("'WEB'"))
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
