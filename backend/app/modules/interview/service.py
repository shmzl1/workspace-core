"""Interview scheduling service."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules._serialization import model_to_dict
from app.modules.interview.repository import InterviewRepository
from app.modules.interview.schemas import ConfirmScheduleRequest, InterviewRead, SchedulePreviewRequest, SchedulePreviewResponse
from app.modules.recruitment.schemas import AdvanceStageRequest
from app.modules.recruitment.service import RecruitmentService
from app.shared.human_only_bridge import HumanOnlyContract, algorithm_not_ready, load_human_only_function


INTERVIEW_SCHEDULER_CONTRACT = HumanOnlyContract(
    module_name="app.human_only.interview_scheduler",
    file_path="backend/app/human_only/interview_scheduler.py",
    function_name="schedule_interview",
    not_ready_message="智能排期服务暂未完成配置",
)


class InterviewService:
    """Orchestrates scheduling preview and persistence around the human-only scheduler."""

    def __init__(self, repository: InterviewRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: Session) -> "InterviewService":
        return cls(InterviewRepository(session))

    def preview_schedule(self, payload: SchedulePreviewRequest) -> SchedulePreviewResponse:
        schedule_interview = self._load_schedule_interview()
        if schedule_interview is None:
            not_ready = algorithm_not_ready(INTERVIEW_SCHEDULER_CONTRACT, {"application_id": payload.application_id})
            return SchedulePreviewResponse(
                status=not_ready["status"], message=not_ready["message"],
                expected_module=not_ready["expected_module"], expected_function=not_ready["expected_function"],
                fallback_data=not_ready["fallback_data"], requires_human_only=True,
            )

        detail = self.repository.get_application_detail(payload.application_id)
        if detail is None:
            raise TalentFlowError("APPLICATION_NOT_FOUND", "候选人申请不存在，无法生成排期预览。")
        application, candidate, _job = detail
        now = datetime.now(timezone.utc)
        candidate_slots = self.repository.list_candidate_slots(candidate.id, ends_after=now)
        if not candidate_slots:
            return SchedulePreviewResponse(
                status="candidate_availability_missing",
                message="该候选人尚未配置有效的面试可用时间，请先配置候选人可用时间后再生成排期建议。",
            )

        interviewer_rows = self.repository.list_interviewers_with_employees()
        interviewer_resources = [
            (
                interviewer,
                employee,
                self.repository.list_interviewer_slots(interviewer.id, ends_after=now),
            )
            for interviewer, employee in interviewer_rows
        ]
        if not any(slots for _interviewer, _employee, slots in interviewer_resources):
            return SchedulePreviewResponse(
                status="interviewer_availability_missing",
                message="当前没有面试官配置有效的可用时间，无法生成排期建议。",
            )

        rooms = self.repository.list_meeting_rooms()
        room_resources = [
            (room, self.repository.list_room_slots(room.id, ends_after=now))
            for room in rooms
        ]
        if not any(slots for _room, slots in room_resources):
            return SchedulePreviewResponse(
                status="room_availability_missing",
                message="当前没有会议室配置有效的可用时间，无法生成排期建议。",
            )

        scheduled_interviews = self.repository.list_scheduled_interviews_with_applications()
        scheduler_payload = {
            "application_id": application.id,
            "duration_minutes": payload.duration_minutes,
            "candidate": {
                "candidate_id": candidate.id,
                "name": candidate.full_name,
                "available_slots": self._slot_rows(candidate_slots),
            },
            "interviewers": [
                {
                    "interviewer_id": interviewer.id,
                    "employee_name": employee.full_name if employee else f"面试官 #{interviewer.id}",
                    "specialties": interviewer.specialties or [],
                    "available_slots": self._slot_rows(slots),
                    "scheduled_count": sum(
                        item.interviewer_id == interviewer.id
                        for item, _app in scheduled_interviews
                    ),
                }
                for interviewer, employee, slots in interviewer_resources
            ],
            "meeting_rooms": [
                {
                    "meeting_room_id": room.id,
                    "room_name": room.name,
                    "available_slots": self._slot_rows(slots),
                }
                for room, slots in room_resources
            ],
            "existing_interviews": [
                {
                    "candidate_id": app.candidate_id,
                    "interviewer_id": interview.interviewer_id,
                    "meeting_room_id": interview.meeting_room_id,
                    "start": interview.start_at.isoformat(),
                    "end": interview.end_at.isoformat(),
                }
                for interview, app in scheduled_interviews
            ],
        }
        result = schedule_interview(scheduler_payload)
        if not isinstance(result, dict):
            raise TalentFlowError("INVALID_SCHEDULE_RESULT", "智能排期结果格式无效。", 500)
        return SchedulePreviewResponse(
            status=result.get("status", "schedule_generated"),
            message=result.get("message", "智能排期建议已生成。"),
            recommended_time=result.get("recommended_time"),
            recommended_interviewer_id=result.get("recommended_interviewer_id"),
            recommended_interviewer=result.get("recommended_interviewer"),
            recommended_room_id=result.get("recommended_room_id"),
            recommended_room=result.get("recommended_room"),
            interviewer_availability=result.get("interviewer_availability"),
            candidate_availability=result.get("candidate_availability"),
            conflict_detection=result.get("conflict_detection"),
            recommendation_reason=result.get("recommendation_reason"),
            conflict_explanation=result.get("conflict_explanation", {}),
            requires_human_only=False,
        )

    def confirm_schedule(self, payload: ConfirmScheduleRequest) -> InterviewRead:
        if payload.end_at <= payload.start_at:
            raise TalentFlowError("INVALID_INTERVIEW_TIME", "面试结束时间必须晚于开始时间。")
        detail = self.repository.get_application_detail(payload.application_id)
        if detail is None:
            raise TalentFlowError("APPLICATION_NOT_FOUND", "候选人申请不存在，无法保存面试。")
        application, candidate, _job = detail
        if self.repository.get_interviewer_with_employee(payload.interviewer_id) is None:
            raise TalentFlowError("INTERVIEWER_NOT_FOUND", "所选面试官不存在或未启用。")
        if self.repository.get_meeting_room(payload.meeting_room_id) is None:
            raise TalentFlowError("MEETING_ROOM_NOT_FOUND", "所选会议室不存在或未启用。")
        if not self.repository.resource_has_available_slot(
            candidate_id=candidate.id,
            interviewer_id=payload.interviewer_id,
            room_id=payload.meeting_room_id,
            start_at=payload.start_at,
            end_at=payload.end_at,
        ):
            raise TalentFlowError("RESOURCE_UNAVAILABLE", "候选人、面试官或会议室在该时间段不可用，请重新生成排期建议。")
        conflicts = self.repository.find_conflicts(
            candidate_id=candidate.id,
            interviewer_id=payload.interviewer_id,
            room_id=payload.meeting_room_id,
            start_at=payload.start_at,
            end_at=payload.end_at,
        )
        if conflicts:
            raise TalentFlowError("INTERVIEW_TIME_CONFLICT", "该时间段已有资源冲突，请重新生成排期建议。", 409)
        interview = self.repository.save_interview(
            application_id=payload.application_id,
            interviewer_id=payload.interviewer_id,
            room_id=payload.meeting_room_id,
            start_at=payload.start_at,
            end_at=payload.end_at,
            conflict_explanation={**payload.conflict_explanation, "confirmation_conflicts": []},
        )
        self._advance_for_scheduled_interview(application.id, application.current_stage)
        return InterviewRead(**model_to_dict(
            interview,
            ["id", "application_id", "interviewer_id", "meeting_room_id", "start_at", "end_at", "status", "conflict_explanation", "created_by_user_id"],
        ))

    def list_interviewers(self) -> list[dict]:
        return [
            {
                **model_to_dict(interviewer, ["id", "employee_id", "specialties", "max_interviews_per_day", "is_active"]),
                "employee_name": employee.full_name if employee else None,
            }
            for interviewer, employee in self.repository.list_interviewers_with_employees()
        ]

    def list_meeting_rooms(self) -> list[dict]:
        return [model_to_dict(room, ["id", "room_code", "name", "location", "capacity", "is_active"]) for room in self.repository.list_meeting_rooms()]

    def list_interviews(self) -> list[dict]:
        return [model_to_dict(
            interview,
            ["id", "application_id", "interviewer_id", "meeting_room_id", "start_at", "end_at", "status", "conflict_explanation", "created_by_user_id"],
        ) for interview in self.repository.list_interviews()]

    def application_ids_with_interviews(self, application_ids: list[int]) -> set[int]:
        selected = set(application_ids)
        return {
            int(interview.application_id)
            for interview in self.repository.list_interviews()
            if interview.application_id in selected
        }

    def _advance_for_scheduled_interview(self, application_id: int, stage: str) -> None:
        paths = {
            "APPLIED": ("AI_SCREENED", "INTERVIEW_PENDING", "INTERVIEWING"),
            "AI_SCREENED": ("INTERVIEW_PENDING", "INTERVIEWING"),
            "INTERVIEW_PENDING": ("INTERVIEWING",),
        }
        for target in paths.get(stage, ()):
            RecruitmentService.from_session(self.repository.session).advance_stage(
                application_id,
                AdvanceStageRequest(to_stage=target, note="面试排期确认后自动推进"),
            )

    @staticmethod
    def _slot_rows(slots: list[Any]) -> list[dict[str, str]]:
        return [{"start": slot.start_at.isoformat(), "end": slot.end_at.isoformat()} for slot in slots]

    @staticmethod
    def _load_schedule_interview() -> Any | None:
        return load_human_only_function(INTERVIEW_SCHEDULER_CONTRACT)
