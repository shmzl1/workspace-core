"""Interview scheduling service."""

from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules._serialization import model_to_dict
from app.modules.interview.repository import InterviewRepository
from app.modules.interview.schemas import SchedulePreviewRequest, SchedulePreviewResponse
from app.shared.human_only_bridge import HumanOnlyContract, algorithm_not_ready, load_human_only_function


INTERVIEW_SCHEDULER_CONTRACT = HumanOnlyContract(
    module_name="app.human_only.interview_scheduler",
    file_path="backend/app/human_only/interview_scheduler.py",
    function_name="schedule_interview",
    not_ready_message="智能排期服务暂未完成配置",
)


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
            not_ready = algorithm_not_ready(
                INTERVIEW_SCHEDULER_CONTRACT,
                {
                    "application_id": payload.application_id,
                    "candidate_slots": len(payload.candidate.available_slots),
                    "interviewer_count": len(payload.interviewers),
                    "meeting_room_count": len(payload.meeting_rooms),
                },
            )
            return SchedulePreviewResponse(
                status=not_ready["status"],
                message=not_ready["message"],
                expected_module=not_ready["expected_module"],
                expected_function=not_ready["expected_function"],
                fallback_data=not_ready["fallback_data"],
                conflict_explanation={
                    "service_entry": "InterviewService.preview_schedule(...)",
                    "candidate_slots": len(payload.candidate.available_slots),
                    "interviewer_count": len(payload.interviewers),
                    "meeting_room_count": len(payload.meeting_rooms),
                },
                requires_human_only=True,
            )

        if not self.repository.application_exists(payload.application_id):
            raise TalentFlowError("APPLICATION_NOT_FOUND", "候选人申请不存在，无法生成排期预览。")

        try:
            scheduler_payload = payload.model_dump(mode="json")
            scheduler_payload["existing_events"] = [
                {"start": interview.start_at.isoformat(), "end": interview.end_at.isoformat()}
                for interview in self.repository.list_interviews()
                if interview.status == "SCHEDULED"
            ]
            result = schedule_interview(scheduler_payload)
        except NotImplementedError:
            not_ready = algorithm_not_ready(
                INTERVIEW_SCHEDULER_CONTRACT,
                {"application_id": payload.application_id},
            )
            return SchedulePreviewResponse(
                status=not_ready["status"],
                message=not_ready["message"],
                expected_module=not_ready["expected_module"],
                expected_function=not_ready["expected_function"],
                fallback_data=not_ready["fallback_data"],
                requires_human_only=True,
            )

        return SchedulePreviewResponse(
            status=result.get("status", "schedule_generated"),
            message=result.get("message", "智能排期建议已生成。"),
            recommended_time=result.get("recommended_time"),
            recommended_interviewer_id=result.get("recommended_interviewer_id"),
            recommended_room_id=result.get("recommended_room_id"),
            interviewer_availability=result.get("interviewer_availability"),
            candidate_availability=result.get("candidate_availability"),
            conflict_detection=result.get("conflict_detection"),
            recommendation_reason=result.get("recommendation_reason"),
            conflict_explanation=result.get("conflict_explanation", {}),
            requires_human_only=False,
        )

    def list_interviewers(self) -> list[dict]:
        results = []
        for interviewer, employee in self.repository.list_interviewers_with_employees():
            item = model_to_dict(
                interviewer,
                ["id", "employee_id", "specialties", "max_interviews_per_day", "is_active"],
            )
            item["employee_name"] = employee.full_name if employee else None
            results.append(item)
        return results

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
        return load_human_only_function(INTERVIEW_SCHEDULER_CONTRACT)
