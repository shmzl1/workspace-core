"""Interview scheduling ORM models."""

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class Interviewer(TimestampMixin, Base):
    """Employee available as an interviewer."""

    __tablename__ = "interviewers"
    __table_args__ = (
        CheckConstraint("max_interviews_per_day > 0", name="ck_interviewers_max_per_day_positive"),
        UniqueConstraint("employee_id", name="uq_interviewers_employee_id"),
        Index("ix_interviewers_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    specialties: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    max_interviews_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=4, server_default=text("4"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))


class MeetingRoom(TimestampMixin, Base):
    """Meeting room for interviews."""

    __tablename__ = "meeting_rooms"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_meeting_rooms_capacity_positive"),
        UniqueConstraint("room_code", name="uq_meeting_rooms_room_code"),
        Index("ix_meeting_rooms_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text("1"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))


class InterviewSlot(TimestampMixin, Base):
    """Availability slot for a candidate, interviewer or room."""

    __tablename__ = "interview_slots"
    __table_args__ = (
        CheckConstraint("resource_type IN ('CANDIDATE', 'INTERVIEWER', 'ROOM')", name="ck_interview_slots_resource_type"),
        CheckConstraint("end_at > start_at", name="ck_interview_slots_time_order"),
        CheckConstraint(
            "((candidate_id IS NOT NULL)::int + (interviewer_id IS NOT NULL)::int + "
            "(meeting_room_id IS NOT NULL)::int) = 1",
            name="ck_interview_slots_exactly_one_resource",
        ),
        CheckConstraint(
            "(resource_type = 'CANDIDATE' AND candidate_id IS NOT NULL AND interviewer_id IS NULL AND meeting_room_id IS NULL) "
            "OR (resource_type = 'INTERVIEWER' AND candidate_id IS NULL AND interviewer_id IS NOT NULL AND meeting_room_id IS NULL) "
            "OR (resource_type = 'ROOM' AND candidate_id IS NULL AND interviewer_id IS NULL AND meeting_room_id IS NOT NULL)",
            name="ck_interview_slots_resource_type_match",
        ),
        Index("ix_interview_slots_candidate_time", "candidate_id", "start_at", "end_at"),
        Index("ix_interview_slots_interviewer_time", "interviewer_id", "start_at", "end_at"),
        Index("ix_interview_slots_room_time", "meeting_room_id", "start_at", "end_at"),
        Index("ix_interview_slots_resource_type", "resource_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False)
    candidate_id: Mapped[int | None] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=True)
    interviewer_id: Mapped[int | None] = mapped_column(ForeignKey("interviewers.id", ondelete="CASCADE"), nullable=True)
    meeting_room_id: Mapped[int | None] = mapped_column(ForeignKey("meeting_rooms.id", ondelete="CASCADE"), nullable=True)
    start_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Interview(TimestampMixin, Base):
    """Scheduled interview."""

    __tablename__ = "interviews"
    __table_args__ = (
        CheckConstraint("end_at > start_at", name="ck_interviews_time_order"),
        CheckConstraint("status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED')", name="ck_interviews_status"),
        Index("ix_interviews_application_id", "application_id"),
        Index("ix_interviews_interviewer_time", "interviewer_id", "start_at", "end_at"),
        Index("ix_interviews_room_time", "meeting_room_id", "start_at", "end_at"),
        Index("ix_interviews_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    interviewer_id: Mapped[int] = mapped_column(ForeignKey("interviewers.id", ondelete="RESTRICT"), nullable=False)
    meeting_room_id: Mapped[int] = mapped_column(ForeignKey("meeting_rooms.id", ondelete="RESTRICT"), nullable=False)
    start_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SCHEDULED", server_default=text("'SCHEDULED'"))
    conflict_explanation: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
