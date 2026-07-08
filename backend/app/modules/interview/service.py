"""Interview scheduling service for Sprint 1 outer workflow."""

from importlib import import_module
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules.interview.repository import InterviewRepository
from app.modules.interview.schemas import SchedulePreviewRequest, SchedulePreviewResponse


class InterviewService:
    """Orchestrates scheduling preview and human-only scheduler calls."""

    def __init__(self, session: Session) -> None:
        self.repository = InterviewRepository(session)

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

    @staticmethod
    def _load_schedule_interview() -> Any | None:
        try:
            module = import_module("app.human_only.interview_scheduler")
        except ModuleNotFoundError:
            return None
        return getattr(module, "schedule_interview", None)
