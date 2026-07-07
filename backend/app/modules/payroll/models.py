"""Payroll ORM models."""

from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class SalaryRecord(TimestampMixin, Base):
    """Employee salary effective record."""

    __tablename__ = "salary_records"
    __table_args__ = (
        CheckConstraint("base_salary >= 0", name="ck_salary_records_base_salary_nonnegative"),
        CheckConstraint("effective_to IS NULL OR effective_to >= effective_from", name="ck_salary_records_effective_range"),
        Index("ix_salary_records_employee_effective_from", "employee_id", "effective_from"),
        Index("ix_salary_records_created_by_user_id", "created_by_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(16), nullable=False, default="CNY", server_default=text("'CNY'"))
    effective_from: Mapped[Date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Date | None] = mapped_column(Date, nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class PayrollPeriod(TimestampMixin, Base):
    """Payroll period for monthly pre-review."""

    __tablename__ = "payroll_periods"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_payroll_periods_date_range"),
        CheckConstraint("standard_work_days > 0", name="ck_payroll_periods_standard_work_days_positive"),
        CheckConstraint("status IN ('OPEN', 'CLOSED')", name="ck_payroll_periods_status"),
        UniqueConstraint("period_code", name="uq_payroll_periods_period_code"),
        Index("ix_payroll_periods_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_code: Mapped[str] = mapped_column(String(32), nullable=False)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date] = mapped_column(Date, nullable=False)
    standard_work_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN", server_default=text("'OPEN'"))


class PayrollRule(TimestampMixin, Base):
    """Payroll calculation rule metadata."""

    __tablename__ = "payroll_rules"
    __table_args__ = (
        CheckConstraint("direction IN ('EARNING', 'DEDUCTION')", name="ck_payroll_rules_direction"),
        CheckConstraint(
            "applies_to IN ('BASE_SALARY', 'PERFORMANCE_BONUS', 'TRANSPORT_ALLOWANCE', "
            "'MEAL_ALLOWANCE', 'ABSENCE', 'LATE', 'EARLY_LEAVE', 'UNPAID_LEAVE')",
            name="ck_payroll_rules_applies_to",
        ),
        CheckConstraint(
            "calculation_method IN ('FIXED_AMOUNT', 'PER_DAY', 'PER_OCCURRENCE', 'MANUAL')",
            name="ck_payroll_rules_calculation_method",
        ),
        UniqueConstraint("rule_code", name="uq_payroll_rules_rule_code"),
        Index("ix_payroll_rules_direction", "direction"),
        Index("ix_payroll_rules_applies_to", "applies_to"),
        Index("ix_payroll_rules_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)
    applies_to: Mapped[str] = mapped_column(String(32), nullable=False)
    calculation_method: Mapped[str] = mapped_column(String(32), nullable=False)
    formula_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))


class PayrollAdjustment(TimestampMixin, Base):
    """Manual or business adjustment for one payroll period."""

    __tablename__ = "payroll_adjustments"
    __table_args__ = (
        CheckConstraint(
            "adjustment_type IN ('PERFORMANCE_BONUS', 'TRANSPORT_ALLOWANCE', 'MEAL_ALLOWANCE', "
            "'MANUAL_EARNING', 'MANUAL_DEDUCTION')",
            name="ck_payroll_adjustments_type",
        ),
        CheckConstraint("amount >= 0", name="ck_payroll_adjustments_amount_nonnegative"),
        Index("ix_payroll_adjustments_employee_period", "employee_id", "payroll_period_id"),
        Index("ix_payroll_adjustments_type", "adjustment_type"),
        Index("ix_payroll_adjustments_created_by_user_id", "created_by_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    payroll_period_id: Mapped[int] = mapped_column(ForeignKey("payroll_periods.id", ondelete="CASCADE"), nullable=False)
    adjustment_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class PayrollReviewRecord(TimestampMixin, Base):
    """Generated payroll pre-review result."""

    __tablename__ = "payroll_review_records"
    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'PRE_AUDIT_GENERATED', 'PENDING_HR_CONFIRMATION', 'CONFIRMED')",
            name="ck_payroll_review_records_status",
        ),
        CheckConstraint("base_salary_snapshot >= 0", name="ck_payroll_review_records_base_salary_nonnegative"),
        CheckConstraint("standard_work_days_snapshot > 0", name="ck_payroll_review_records_work_days_positive"),
        CheckConstraint("total_earnings >= 0", name="ck_payroll_review_records_earnings_nonnegative"),
        CheckConstraint("total_deductions >= 0", name="ck_payroll_review_records_deductions_nonnegative"),
        CheckConstraint("net_salary_preview >= 0", name="ck_payroll_review_records_net_nonnegative"),
        CheckConstraint(
            "(status <> 'CONFIRMED') OR (confirmed_by_user_id IS NOT NULL AND confirmed_at IS NOT NULL)",
            name="ck_payroll_review_records_confirmed_fields",
        ),
        UniqueConstraint("employee_id", "payroll_period_id", name="uq_payroll_review_records_employee_period"),
        Index("ix_payroll_review_records_employee_period", "employee_id", "payroll_period_id"),
        Index("ix_payroll_review_records_status", "status"),
        Index("ix_payroll_review_records_generated_by_user_id", "generated_by_user_id"),
        Index("ix_payroll_review_records_confirmed_by_user_id", "confirmed_by_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    payroll_period_id: Mapped[int] = mapped_column(ForeignKey("payroll_periods.id", ondelete="CASCADE"), nullable=False)
    salary_record_id: Mapped[int | None] = mapped_column(ForeignKey("salary_records.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT", server_default=text("'DRAFT'"))
    base_salary_snapshot: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    standard_work_days_snapshot: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    calculation_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    total_earnings: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"), server_default=text("0"))
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"), server_default=text("0"))
    net_salary_preview: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"), server_default=text("0"))
    generated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PayrollLineItem(Base):
    """Line item that explains a payroll review result."""

    __tablename__ = "payroll_line_items"
    __table_args__ = (
        CheckConstraint("item_type IN ('EARNING', 'DEDUCTION')", name="ck_payroll_line_items_item_type"),
        CheckConstraint(
            "source_type IS NULL OR source_type IN ('ATTENDANCE', 'PAYROLL_ADJUSTMENT', 'MANUAL', 'RULE')",
            name="ck_payroll_line_items_source_type",
        ),
        CheckConstraint("amount >= 0", name="ck_payroll_line_items_amount_nonnegative"),
        Index("ix_payroll_line_items_review_record_id", "payroll_review_record_id"),
        Index("ix_payroll_line_items_payroll_rule_id", "payroll_rule_id"),
        Index("ix_payroll_line_items_source_type", "source_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payroll_review_record_id: Mapped[int] = mapped_column(
        ForeignKey("payroll_review_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    payroll_rule_id: Mapped[int | None] = mapped_column(ForeignKey("payroll_rules.id", ondelete="SET NULL"), nullable=True)
    item_type: Mapped[str] = mapped_column(String(32), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_reference_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    calculation_detail_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
