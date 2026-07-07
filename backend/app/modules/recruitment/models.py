"""Recruitment ORM models."""

from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin

PIPELINE_STAGES = (
    "'APPLIED', 'AI_SCREENED', 'INTERVIEW_PENDING', 'INTERVIEWING', "
    "'DECISION_PENDING', 'OFFERED', 'HIRED', 'REJECTED'"
)


class Job(TimestampMixin, Base):
    """Recruitment job opening."""

    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("min_experience_months >= 0", name="ck_jobs_min_experience_nonnegative"),
        CheckConstraint("employment_type IN ('INTERN', 'FULL_TIME', 'PART_TIME')", name="ck_jobs_employment_type"),
        CheckConstraint("status IN ('DRAFT', 'OPEN', 'CLOSED')", name="ck_jobs_status"),
        UniqueConstraint("job_code", name="uq_jobs_job_code"),
        Index("ix_jobs_department", "department"),
        Index("ix_jobs_status", "status"),
        Index("ix_jobs_owner_user_id", "owner_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_code: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    preferred_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    min_experience_months: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employment_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="INTERN",
        server_default=text("'INTERN'"),
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT", server_default=text("'DRAFT'"))
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class Candidate(TimestampMixin, Base):
    """Candidate profile and parsed resume fields."""

    __tablename__ = "candidates"
    __table_args__ = (
        CheckConstraint("experience_months >= 0", name="ck_candidates_experience_nonnegative"),
        CheckConstraint("source IN ('MANUAL', 'UPLOAD', 'SEED', 'REFERRAL')", name="ck_candidates_source"),
        UniqueConstraint("candidate_no", name="uq_candidates_candidate_no"),
        UniqueConstraint("email", name="uq_candidates_email"),
        UniqueConstraint("phone", name="uq_candidates_phone"),
        Index("ix_candidates_available_from", "available_from"),
        Index("ix_candidates_source", "source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    candidate_no: Mapped[str] = mapped_column(String(32), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    resume_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    experience_months: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    available_from: Mapped[Date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="MANUAL", server_default=text("'MANUAL'"))
    profile_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))


class CandidateApplication(Base):
    """Candidate application for one job."""

    __tablename__ = "candidate_applications"
    __table_args__ = (
        CheckConstraint(f"current_stage IN ({PIPELINE_STAGES})", name="ck_candidate_applications_current_stage"),
        CheckConstraint("score_total IS NULL OR score_total >= 0", name="ck_candidate_applications_score_nonnegative"),
        UniqueConstraint("candidate_id", "job_id", name="uq_candidate_applications_candidate_job"),
        Index("ix_candidate_applications_job_stage", "job_id", "current_stage"),
        Index("ix_candidate_applications_candidate_id", "candidate_id"),
        Index("ix_candidate_applications_score_total", "score_total"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    current_stage: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="APPLIED",
        server_default=text("'APPLIED'"),
    )
    score_total: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    score_breakdown: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    weights_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    scored_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    applied_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class CandidatePipelineRecord(Base):
    """Recruitment pipeline transition record."""

    __tablename__ = "candidate_pipeline_records"
    __table_args__ = (
        CheckConstraint(f"from_stage IS NULL OR from_stage IN ({PIPELINE_STAGES})", name="ck_pipeline_records_from_stage"),
        CheckConstraint(f"to_stage IN ({PIPELINE_STAGES})", name="ck_pipeline_records_to_stage"),
        Index("ix_pipeline_records_application_created_at", "application_id", "created_at"),
        Index("ix_pipeline_records_changed_by_user_id", "changed_by_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    from_stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_stage: Mapped[str] = mapped_column(String(32), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
