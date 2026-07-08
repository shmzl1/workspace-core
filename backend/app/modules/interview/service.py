"""Interview scheduling service for Sprint 1 outer workflow."""

from importlib import import_module
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules._serialization import model_to_dict
from app.modules.interview.repository import InterviewRepository
from app.modules.interview.schemas import SchedulePreviewRequest, SchedulePreviewResponse


class InterviewService:
    """Orchestrates scheduling preview and human-only scheduler calls."""

    def __init__(self, repository: InterviewRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: Session) -> "InterviewService":
        return cls(InterviewRepository(session))

    def preview_schedule(self, payload: SchedulePreviewRequest) -> SchedulePreviewResponse:
        schedule_interview = self._load_schedule_interview()
        if schedule_interview is None:
            return SchedulePreviewResponse(
                status="HUMAN_ONLY_ALGORITHM_NOT_READY",
                message="面试排期禁飞区尚未由黄钧人工接入。",
                conflict_explanation={
                    "expected_entry": "backend/app/human_only/interview_scheduler.py::schedule_interview(...)",
                    "service_entry": "InterviewService.preview_schedule(...)",
                    "candidate_slots": len(payload.candidate.available_slots),
                    "interviewer_count": len(payload.interviewers),
                    "meeting_room_count": len(payload.meeting_rooms),
                },
                requires_human_only=True,
            )

        if not self.repository.application_exists(payload.application_id):
            raise TalentFlowError("APPLICATION_NOT_FOUND", "候选人申请不存在，无法生成排期预览。")

        result = schedule_interview(payload.model_dump(mode="json"))
        return SchedulePreviewResponse(
            status=result.get("status", "PREVIEW_GENERATED"),
            message=result.get("message", "排期预览已由禁飞区公开函数返回。"),
            recommended_time=result.get("recommended_time"),
            recommended_interviewer_id=result.get("recommended_interviewer_id"),
            recommended_room_id=result.get("recommended_room_id"),
            conflict_explanation=result.get("conflict_explanation", {}),
            requires_human_only=False,
        )

    def list_interviewers(self) -> list[dict]:
        return [
            model_to_dict(interviewer, ["id", "employee_id", "specialties", "max_interviews_per_day", "is_active"])
            for interviewer in self.repository.list_interviewers()
        ]

    def list_meeting_rooms(self) -> list[dict]:
        return [
            model_to_dict(room, ["id", "room_code", "name", "location", "capacity", "is_active"])
            for room in self.repository.list_meeting_rooms()
        ]

    def list_interviews(self) -> list[dict]:
        return [
            model_to_dict(
                interview,
                [
                    "id",
                    "application_id",
                    "interviewer_id",
                    "meeting_room_id",
                    "start_at",
                    "end_at",
                    "status",
                    "conflict_explanation",
                    "created_by_user_id",
                ],
            )
            for interview in self.repository.list_interviews()
        ]

    @staticmethod
    def _load_schedule_interview() -> Any | None:
        try:
            module = import_module("app.human_only.interview_scheduler")
        except ModuleNotFoundError:
            return None
        return getattr(module, "schedule_interview", None)
