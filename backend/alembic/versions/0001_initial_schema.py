"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-07
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamps(),
        sa.CheckConstraint(
            "role IN ('EMPLOYEE', 'HR_SPECIALIST', 'DEPARTMENT_MANAGER', 'PAYROLL_ADMIN')",
            name="ck_users_role",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("employee_no", sa.String(length=32), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("job_title", sa.String(length=100), nullable=False),
        sa.Column("manager_employee_id", sa.Integer(), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column("employment_status", sa.String(length=32), server_default=sa.text("'ACTIVE'"), nullable=False),
        *timestamps(),
        sa.CheckConstraint(
            "employment_status IN ('ACTIVE', 'INACTIVE', 'ON_LEAVE')",
            name="ck_employees_employment_status",
        ),
        sa.ForeignKeyConstraint(["manager_employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_no", name="uq_employees_employee_no"),
        sa.UniqueConstraint("email", name="uq_employees_email"),
        sa.UniqueConstraint("phone", name="uq_employees_phone"),
        sa.UniqueConstraint("user_id", name="uq_employees_user_id"),
    )
    op.create_index("ix_employees_department", "employees", ["department"])
    op.create_index("ix_employees_manager_employee_id", "employees", ["manager_employee_id"])
    op.create_index("ix_employees_employment_status", "employees", ["employment_status"])

    op.create_table(
        "leave_balances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("leave_type", sa.String(length=32), server_default=sa.text("'ANNUAL'"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("total_days", sa.Numeric(5, 2), nullable=False),
        sa.Column("used_days", sa.Numeric(5, 2), server_default=sa.text("0"), nullable=False),
        *timestamps(),
        sa.CheckConstraint("leave_type IN ('ANNUAL')", name="ck_leave_balances_leave_type"),
        sa.CheckConstraint("total_days >= 0", name="ck_leave_balances_total_days_nonnegative"),
        sa.CheckConstraint("used_days >= 0", name="ck_leave_balances_used_days_nonnegative"),
        sa.CheckConstraint("used_days <= total_days", name="ck_leave_balances_used_days_lte_total"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", "year", "leave_type", name="uq_leave_balances_employee_year_type"),
    )
    op.create_index("ix_leave_balances_employee_year", "leave_balances", ["employee_id", "year"])

    op.create_table(
        "work_calendars",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("calendar_date", sa.Date(), nullable=False),
        sa.Column("is_workday", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("standard_check_in_time", sa.Time(), server_default=sa.text("'09:00:00'"), nullable=False),
        sa.Column("standard_check_out_time", sa.Time(), server_default=sa.text("'18:00:00'"), nullable=False),
        sa.Column("late_grace_minutes", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("holiday_name", sa.String(length=100), nullable=True),
        sa.Column("remark", sa.String(length=255), nullable=True),
        *timestamps(),
        sa.CheckConstraint("late_grace_minutes >= 0", name="ck_work_calendars_late_grace_nonnegative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("calendar_date", name="uq_work_calendars_date"),
    )
    op.create_index("ix_work_calendars_is_workday", "work_calendars", ["is_workday"])

    op.create_table(
        "attendance_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("check_in_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("check_out_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'NORMAL'"), nullable=False),
        sa.Column("late_minutes", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("early_leave_minutes", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("leave_balance_id", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=32), server_default=sa.text("'WEB'"), nullable=False),
        sa.Column("remark", sa.String(length=255), nullable=True),
        *timestamps(),
        sa.CheckConstraint(
            "status IN ('NORMAL', 'LATE', 'EARLY_LEAVE', 'ABSENT', 'UNPAID_LEAVE', 'APPROVED_ANNUAL_LEAVE')",
            name="ck_attendance_records_status",
        ),
        sa.CheckConstraint("source IN ('WEB', 'MINIPROGRAM', 'MANUAL', 'SEED')", name="ck_attendance_records_source"),
        sa.CheckConstraint("late_minutes >= 0", name="ck_attendance_records_late_minutes_nonnegative"),
        sa.CheckConstraint("early_leave_minutes >= 0", name="ck_attendance_records_early_leave_minutes_nonnegative"),
        sa.CheckConstraint(
            "check_out_at IS NULL OR check_in_at IS NULL OR check_out_at > check_in_at",
            name="ck_attendance_records_checkout_after_checkin",
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["leave_balance_id"], ["leave_balances.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", "attendance_date", name="uq_attendance_records_employee_date"),
    )
    op.create_index("ix_attendance_records_employee_date", "attendance_records", ["employee_id", "attendance_date"])
    op.create_index("ix_attendance_records_status", "attendance_records", ["status"])
    op.create_index("ix_attendance_records_attendance_date", "attendance_records", ["attendance_date"])

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_code", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("required_skills", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("preferred_skills", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("min_experience_months", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("employment_type", sa.String(length=32), server_default=sa.text("'INTERN'"), nullable=False),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        *timestamps(),
        sa.CheckConstraint("min_experience_months >= 0", name="ck_jobs_min_experience_nonnegative"),
        sa.CheckConstraint("employment_type IN ('INTERN', 'FULL_TIME', 'PART_TIME')", name="ck_jobs_employment_type"),
        sa.CheckConstraint("status IN ('DRAFT', 'OPEN', 'CLOSED')", name="ck_jobs_status"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_code", name="uq_jobs_job_code"),
    )
    op.create_index("ix_jobs_department", "jobs", ["department"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_owner_user_id", "jobs", ["owner_user_id"])

    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_no", sa.String(length=32), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("resume_file_path", sa.String(length=500), nullable=True),
        sa.Column("resume_text", sa.Text(), nullable=True),
        sa.Column("skills", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("experience_months", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("available_from", sa.Date(), nullable=True),
        sa.Column("source", sa.String(length=32), server_default=sa.text("'MANUAL'"), nullable=False),
        sa.Column("profile_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        *timestamps(),
        sa.CheckConstraint("experience_months >= 0", name="ck_candidates_experience_nonnegative"),
        sa.CheckConstraint("source IN ('MANUAL', 'UPLOAD', 'SEED', 'REFERRAL')", name="ck_candidates_source"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_no", name="uq_candidates_candidate_no"),
        sa.UniqueConstraint("email", name="uq_candidates_email"),
        sa.UniqueConstraint("phone", name="uq_candidates_phone"),
    )
    op.create_index("ix_candidates_available_from", "candidates", ["available_from"])
    op.create_index("ix_candidates_source", "candidates", ["source"])

    stage_check = (
        "'APPLIED', 'AI_SCREENED', 'INTERVIEW_PENDING', 'INTERVIEWING', "
        "'DECISION_PENDING', 'OFFERED', 'HIRED', 'REJECTED'"
    )
    op.create_table(
        "candidate_applications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("current_stage", sa.String(length=32), server_default=sa.text("'APPLIED'"), nullable=False),
        sa.Column("score_total", sa.Numeric(6, 2), nullable=True),
        sa.Column("score_breakdown", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("weights_snapshot", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("scored_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(f"current_stage IN ({stage_check})", name="ck_candidate_applications_current_stage"),
        sa.CheckConstraint("score_total IS NULL OR score_total >= 0", name="ck_candidate_applications_score_nonnegative"),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id", "job_id", name="uq_candidate_applications_candidate_job"),
    )
    op.create_index("ix_candidate_applications_job_stage", "candidate_applications", ["job_id", "current_stage"])
    op.create_index("ix_candidate_applications_candidate_id", "candidate_applications", ["candidate_id"])
    op.create_index("ix_candidate_applications_score_total", "candidate_applications", ["score_total"])

    op.create_table(
        "candidate_pipeline_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("from_stage", sa.String(length=32), nullable=True),
        sa.Column("to_stage", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("changed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(f"from_stage IS NULL OR from_stage IN ({stage_check})", name="ck_pipeline_records_from_stage"),
        sa.CheckConstraint(f"to_stage IN ({stage_check})", name="ck_pipeline_records_to_stage"),
        sa.ForeignKeyConstraint(["application_id"], ["candidate_applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pipeline_records_application_created_at", "candidate_pipeline_records", ["application_id", "created_at"])
    op.create_index("ix_pipeline_records_changed_by_user_id", "candidate_pipeline_records", ["changed_by_user_id"])

    op.create_table(
        "interviewers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("specialties", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("max_interviews_per_day", sa.Integer(), server_default=sa.text("4"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamps(),
        sa.CheckConstraint("max_interviews_per_day > 0", name="ck_interviewers_max_per_day_positive"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", name="uq_interviewers_employee_id"),
    )
    op.create_index("ix_interviewers_is_active", "interviewers", ["is_active"])

    op.create_table(
        "meeting_rooms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("capacity", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamps(),
        sa.CheckConstraint("capacity > 0", name="ck_meeting_rooms_capacity_positive"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_code", name="uq_meeting_rooms_room_code"),
    )
    op.create_index("ix_meeting_rooms_is_active", "meeting_rooms", ["is_active"])

    op.create_table(
        "interview_slots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("resource_type", sa.String(length=32), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=True),
        sa.Column("interviewer_id", sa.Integer(), nullable=True),
        sa.Column("meeting_room_id", sa.Integer(), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_available", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        *timestamps(),
        sa.CheckConstraint("resource_type IN ('CANDIDATE', 'INTERVIEWER', 'ROOM')", name="ck_interview_slots_resource_type"),
        sa.CheckConstraint("end_at > start_at", name="ck_interview_slots_time_order"),
        sa.CheckConstraint(
            "((candidate_id IS NOT NULL)::int + (interviewer_id IS NOT NULL)::int + "
            "(meeting_room_id IS NOT NULL)::int) = 1",
            name="ck_interview_slots_exactly_one_resource",
        ),
        sa.CheckConstraint(
            "(resource_type = 'CANDIDATE' AND candidate_id IS NOT NULL AND interviewer_id IS NULL AND meeting_room_id IS NULL) "
            "OR (resource_type = 'INTERVIEWER' AND candidate_id IS NULL AND interviewer_id IS NOT NULL AND meeting_room_id IS NULL) "
            "OR (resource_type = 'ROOM' AND candidate_id IS NULL AND interviewer_id IS NULL AND meeting_room_id IS NOT NULL)",
            name="ck_interview_slots_resource_type_match",
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interviewer_id"], ["interviewers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["meeting_room_id"], ["meeting_rooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_interview_slots_candidate_time", "interview_slots", ["candidate_id", "start_at", "end_at"])
    op.create_index("ix_interview_slots_interviewer_time", "interview_slots", ["interviewer_id", "start_at", "end_at"])
    op.create_index("ix_interview_slots_room_time", "interview_slots", ["meeting_room_id", "start_at", "end_at"])
    op.create_index("ix_interview_slots_resource_type", "interview_slots", ["resource_type"])

    op.create_table(
        "interviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("interviewer_id", sa.Integer(), nullable=False),
        sa.Column("meeting_room_id", sa.Integer(), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'SCHEDULED'"), nullable=False),
        sa.Column("conflict_explanation", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        *timestamps(),
        sa.CheckConstraint("end_at > start_at", name="ck_interviews_time_order"),
        sa.CheckConstraint("status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED')", name="ck_interviews_status"),
        sa.ForeignKeyConstraint(["application_id"], ["candidate_applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["interviewer_id"], ["interviewers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["meeting_room_id"], ["meeting_rooms.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_interviews_application_id", "interviews", ["application_id"])
    op.create_index("ix_interviews_interviewer_time", "interviews", ["interviewer_id", "start_at", "end_at"])
    op.create_index("ix_interviews_room_time", "interviews", ["meeting_room_id", "start_at", "end_at"])
    op.create_index("ix_interviews_status", "interviews", ["status"])

    op.create_table(
        "salary_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("base_salary", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=16), server_default=sa.text("'CNY'"), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        *timestamps(),
        sa.CheckConstraint("base_salary >= 0", name="ck_salary_records_base_salary_nonnegative"),
        sa.CheckConstraint("effective_to IS NULL OR effective_to >= effective_from", name="ck_salary_records_effective_range"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_salary_records_employee_effective_from", "salary_records", ["employee_id", "effective_from"])
    op.create_index("ix_salary_records_created_by_user_id", "salary_records", ["created_by_user_id"])

    op.create_table(
        "payroll_periods",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("period_code", sa.String(length=32), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("standard_work_days", sa.Numeric(5, 2), nullable=False),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'OPEN'"), nullable=False),
        *timestamps(),
        sa.CheckConstraint("end_date >= start_date", name="ck_payroll_periods_date_range"),
        sa.CheckConstraint("standard_work_days > 0", name="ck_payroll_periods_standard_work_days_positive"),
        sa.CheckConstraint("status IN ('OPEN', 'CLOSED')", name="ck_payroll_periods_status"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("period_code", name="uq_payroll_periods_period_code"),
    )
    op.create_index("ix_payroll_periods_status", "payroll_periods", ["status"])

    op.create_table(
        "payroll_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("direction", sa.String(length=16), nullable=False),
        sa.Column("applies_to", sa.String(length=32), nullable=False),
        sa.Column("calculation_method", sa.String(length=32), nullable=False),
        sa.Column("formula_description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamps(),
        sa.CheckConstraint("direction IN ('EARNING', 'DEDUCTION')", name="ck_payroll_rules_direction"),
        sa.CheckConstraint(
            "applies_to IN ('BASE_SALARY', 'PERFORMANCE_BONUS', 'TRANSPORT_ALLOWANCE', "
            "'MEAL_ALLOWANCE', 'ABSENCE', 'LATE', 'EARLY_LEAVE', 'UNPAID_LEAVE')",
            name="ck_payroll_rules_applies_to",
        ),
        sa.CheckConstraint(
            "calculation_method IN ('FIXED_AMOUNT', 'PER_DAY', 'PER_OCCURRENCE', 'MANUAL')",
            name="ck_payroll_rules_calculation_method",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rule_code", name="uq_payroll_rules_rule_code"),
    )
    op.create_index("ix_payroll_rules_direction", "payroll_rules", ["direction"])
    op.create_index("ix_payroll_rules_applies_to", "payroll_rules", ["applies_to"])
    op.create_index("ix_payroll_rules_is_active", "payroll_rules", ["is_active"])

    op.create_table(
        "payroll_adjustments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("payroll_period_id", sa.Integer(), nullable=False),
        sa.Column("adjustment_type", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        *timestamps(),
        sa.CheckConstraint(
            "adjustment_type IN ('PERFORMANCE_BONUS', 'TRANSPORT_ALLOWANCE', 'MEAL_ALLOWANCE', "
            "'MANUAL_EARNING', 'MANUAL_DEDUCTION')",
            name="ck_payroll_adjustments_type",
        ),
        sa.CheckConstraint("amount >= 0", name="ck_payroll_adjustments_amount_nonnegative"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payroll_period_id"], ["payroll_periods.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payroll_adjustments_employee_period", "payroll_adjustments", ["employee_id", "payroll_period_id"])
    op.create_index("ix_payroll_adjustments_type", "payroll_adjustments", ["adjustment_type"])
    op.create_index("ix_payroll_adjustments_created_by_user_id", "payroll_adjustments", ["created_by_user_id"])

    op.create_table(
        "payroll_review_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("payroll_period_id", sa.Integer(), nullable=False),
        sa.Column("salary_record_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("base_salary_snapshot", sa.Numeric(12, 2), nullable=False),
        sa.Column("standard_work_days_snapshot", sa.Numeric(5, 2), nullable=False),
        sa.Column("calculation_snapshot", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("total_earnings", sa.Numeric(12, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("total_deductions", sa.Numeric(12, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("net_salary_preview", sa.Numeric(12, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("generated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("confirmed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PRE_AUDIT_GENERATED', 'PENDING_HR_CONFIRMATION', 'CONFIRMED')",
            name="ck_payroll_review_records_status",
        ),
        sa.CheckConstraint("base_salary_snapshot >= 0", name="ck_payroll_review_records_base_salary_nonnegative"),
        sa.CheckConstraint("standard_work_days_snapshot > 0", name="ck_payroll_review_records_work_days_positive"),
        sa.CheckConstraint("total_earnings >= 0", name="ck_payroll_review_records_earnings_nonnegative"),
        sa.CheckConstraint("total_deductions >= 0", name="ck_payroll_review_records_deductions_nonnegative"),
        sa.CheckConstraint("net_salary_preview >= 0", name="ck_payroll_review_records_net_nonnegative"),
        sa.CheckConstraint(
            "(status <> 'CONFIRMED') OR (confirmed_by_user_id IS NOT NULL AND confirmed_at IS NOT NULL)",
            name="ck_payroll_review_records_confirmed_fields",
        ),
        sa.ForeignKeyConstraint(["confirmed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["generated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["payroll_period_id"], ["payroll_periods.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["salary_record_id"], ["salary_records.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", "payroll_period_id", name="uq_payroll_review_records_employee_period"),
    )
    op.create_index("ix_payroll_review_records_employee_period", "payroll_review_records", ["employee_id", "payroll_period_id"])
    op.create_index("ix_payroll_review_records_status", "payroll_review_records", ["status"])
    op.create_index("ix_payroll_review_records_generated_by_user_id", "payroll_review_records", ["generated_by_user_id"])
    op.create_index("ix_payroll_review_records_confirmed_by_user_id", "payroll_review_records", ["confirmed_by_user_id"])

    op.create_table(
        "payroll_line_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("payroll_review_record_id", sa.Integer(), nullable=False),
        sa.Column("payroll_rule_id", sa.Integer(), nullable=True),
        sa.Column("item_type", sa.String(length=32), nullable=False),
        sa.Column("item_name", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=True),
        sa.Column("source_reference_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("calculation_detail_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("item_type IN ('EARNING', 'DEDUCTION')", name="ck_payroll_line_items_item_type"),
        sa.CheckConstraint(
            "source_type IS NULL OR source_type IN ('ATTENDANCE', 'PAYROLL_ADJUSTMENT', 'MANUAL', 'RULE')",
            name="ck_payroll_line_items_source_type",
        ),
        sa.CheckConstraint("amount >= 0", name="ck_payroll_line_items_amount_nonnegative"),
        sa.ForeignKeyConstraint(["payroll_review_record_id"], ["payroll_review_records.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payroll_rule_id"], ["payroll_rules.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payroll_line_items_review_record_id", "payroll_line_items", ["payroll_review_record_id"])
    op.create_index("ix_payroll_line_items_payroll_rule_id", "payroll_line_items", ["payroll_rule_id"])
    op.create_index("ix_payroll_line_items_source_type", "payroll_line_items", ["source_type"])

    op.create_table(
        "policy_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("source_path", sa.String(length=500), nullable=True),
        sa.Column("version", sa.String(length=32), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_code", name="uq_policy_documents_document_code"),
    )
    op.create_index("ix_policy_documents_category", "policy_documents", ["category"])
    op.create_index("ix_policy_documents_is_active", "policy_documents", ["is_active"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("actor_role", sa.String(length=32), nullable=False),
        sa.Column("target_employee_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("requested_fields", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("result", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("trace_id", sa.String(length=64), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "actor_role IN ('EMPLOYEE', 'HR_SPECIALIST', 'DEPARTMENT_MANAGER', 'PAYROLL_ADMIN')",
            name="ck_audit_logs_actor_role",
        ),
        sa.CheckConstraint("result IN ('ALLOWED', 'DENIED', 'SUCCESS', 'FAILURE')", name="ck_audit_logs_result"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_actor_created_at", "audit_logs", ["actor_user_id", "created_at"])
    op.create_index("ix_audit_logs_target_employee_created_at", "audit_logs", ["target_employee_id", "created_at"])
    op.create_index("ix_audit_logs_trace_id", "audit_logs", ["trace_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_read_created_at", "notifications", ["user_id", "is_read", "created_at"])
    op.create_index("ix_notifications_notification_type", "notifications", ["notification_type"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("audit_logs")
    op.drop_table("policy_documents")
    op.drop_table("payroll_line_items")
    op.drop_table("payroll_review_records")
    op.drop_table("payroll_adjustments")
    op.drop_table("payroll_rules")
    op.drop_table("payroll_periods")
    op.drop_table("salary_records")
    op.drop_table("interviews")
    op.drop_table("interview_slots")
    op.drop_table("meeting_rooms")
    op.drop_table("interviewers")
    op.drop_table("candidate_pipeline_records")
    op.drop_table("candidate_applications")
    op.drop_table("candidates")
    op.drop_table("jobs")
    op.drop_table("attendance_records")
    op.drop_table("work_calendars")
    op.drop_table("leave_balances")
    op.drop_table("employees")
    op.drop_table("users")
