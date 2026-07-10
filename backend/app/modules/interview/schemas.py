"""Interview scheduling schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SchedulePreviewRequest(BaseModel):
    application_id: int
    duration_minutes: int = Field(default=60, ge=30, le=240)


class SchedulePreviewResponse(BaseModel):
    status: str
    message: str
    recommended_time: dict[str, Any] | None = None
    recommended_interviewer_id: int | None = None
    recommended_interviewer: str | None = None
    recommended_room_id: int | None = None
    recommended_room: str | None = None
    interviewer_availability: str | None = None
    candidate_availability: str | None = None
    conflict_detection: str | None = None
    recommendation_reason: str | None = None
    conflict_explanation: dict[str, object] = Field(default_factory=dict)
    expected_module: str | None = None
    expected_function: str | None = None
    fallback_data: dict[str, Any] = Field(default_factory=dict)
    requires_human_only: bool = False


class ConfirmScheduleRequest(BaseModel):
    application_id: int
    interviewer_id: int
    meeting_room_id: int
    start_at: datetime
    end_at: datetime
    conflict_explanation: dict[str, Any] = Field(default_factory=dict)


class InterviewRead(BaseModel):
    id: int
    application_id: int
    interviewer_id: int
    meeting_room_id: int
    start_at: datetime
    end_at: datetime
    status: str
    conflict_explanation: dict[str, Any] = Field(default_factory=dict)
    created_by_user_id: int | None = None
