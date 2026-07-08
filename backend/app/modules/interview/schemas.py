"""Interview scheduling schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CandidateAvailability(BaseModel):
    candidate_id: int
    available_slots: list[dict[str, datetime]] = Field(default_factory=list)


class InterviewerOption(BaseModel):
    interviewer_id: int
    employee_name: str | None = None
    specialties: list[str] = Field(default_factory=list)
    available_slots: list[dict[str, datetime]] = Field(default_factory=list)


class MeetingRoomOption(BaseModel):
    meeting_room_id: int
    room_name: str | None = None
    available_slots: list[dict[str, datetime]] = Field(default_factory=list)


class SchedulePreviewRequest(BaseModel):
    application_id: int
    candidate: CandidateAvailability
    interviewers: list[InterviewerOption] = Field(default_factory=list)
    meeting_rooms: list[MeetingRoomOption] = Field(default_factory=list)
    duration_minutes: int = 60


class SchedulePreviewResponse(BaseModel):
    status: str
    message: str
    recommended_time: dict[str, Any] | None = None
    recommended_interviewer_id: int | None = None
    recommended_room_id: int | None = None
    interviewer_availability: str | None = None
    candidate_availability: str | None = None
    conflict_detection: str | None = None
    recommendation_reason: str | None = None
    conflict_explanation: dict[str, object] = Field(default_factory=dict)
    expected_module: str | None = None
    expected_function: str | None = None
    fallback_data: dict[str, Any] = Field(default_factory=dict)
    requires_human_only: bool = False
