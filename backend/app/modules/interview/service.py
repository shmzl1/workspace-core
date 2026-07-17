"""Interview scheduling service."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules._serialization import model_to_dict
from app.modules.interview.repository import InterviewRepository
from app.modules.interview.schemas import (
    AvailabilityBatchResult,
    AvailabilityBatchWrite,
    AvailabilitySlotWrite,
    ConfirmScheduleRequest,
    InterviewRead,
    SchedulePreviewRequest,
    SchedulePreviewResponse,
)
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
        if payload.interviewer_ids is not None and not payload.interviewer_ids:
            raise TalentFlowError("INTERVIEWER_REQUIRED", "请至少选择一名面试官后再生成排期预览。")
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
        if payload.interviewer_ids is not None:
            selected_interviewer_ids = set(payload.interviewer_ids)
            active_interviewer_ids = {interviewer.id for interviewer, _employee in interviewer_rows}
            missing_ids = selected_interviewer_ids - active_interviewer_ids
            if missing_ids:
                raise TalentFlowError(
                    "INTERVIEWER_NOT_FOUND",
                    f"面试官编号 {', '.join(map(str, sorted(missing_ids)))} 不存在或未启用。",
                )
            interviewer_rows = [
                (interviewer, employee)
                for interviewer, employee in interviewer_rows
                if interviewer.id in selected_interviewer_ids
            ]
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
        if not rooms:
            return SchedulePreviewResponse(
                status="room_availability_missing",
                message="当前没有启用的会议室资源，无法生成排期建议。",
            )
        # 启用会议室默认全时可用，候选人的可用窗口不会被 ROOM 时间槽额外收窄。
        # 已有面试仍通过 existing_interviews 和确认阶段冲突检查避免重复占用。
        room_resources = [(room, candidate_slots) for room in rooms]

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
        conflict_explanation = result.get("conflict_explanation")
        if not isinstance(conflict_explanation, dict):
            conflict_explanation = {}
        best_slot = result.get("best_slot")
        recommended_slot_conflict = (
            bool(best_slot.get("conflict", False))
            if isinstance(best_slot, dict)
            else bool(conflict_explanation.get("recommended_slot_conflict", False))
        )
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
            conflict_explanation={
                **conflict_explanation,
                "recommended_slot_conflict": recommended_slot_conflict,
            },
            requires_human_only=False,
        )

    def save_availability(self, payload: AvailabilityBatchWrite) -> AvailabilityBatchResult:
        if not payload.candidates and not payload.interviewers:
            raise TalentFlowError("AVAILABILITY_REQUIRED", "请至少提交一名候选人或面试官的空闲时间。")

        candidate_ids = [item.candidate_id for item in payload.candidates]
        interviewer_ids = [item.interviewer_id for item in payload.interviewers]
        self._ensure_unique_resource_ids(candidate_ids, "候选人")
        self._ensure_unique_resource_ids(interviewer_ids, "面试官")

        for candidate_id in candidate_ids:
            if self.repository.get_candidate(candidate_id) is None:
                raise TalentFlowError("CANDIDATE_NOT_FOUND", f"候选人编号 {candidate_id} 不存在。")
        for interviewer_id in interviewer_ids:
            if self.repository.get_interviewer_with_employee(interviewer_id) is None:
                raise TalentFlowError(
                    "INTERVIEWER_NOT_FOUND",
                    f"面试官编号 {interviewer_id} 不存在或未启用。",
                )

        now = datetime.now(timezone.utc)
        candidate_slots = {
            item.candidate_id: self._validate_availability_slots(
                item.slots,
                f"候选人编号 {item.candidate_id}",
                now,
                item.duration_minutes,
            )
            for item in payload.candidates
        }
        interviewer_minimum_minutes = max(
            (item.duration_minutes for item in payload.candidates),
            default=60,
        )
        interviewer_slots = {
            item.interviewer_id: self._validate_availability_slots(
                item.slots,
                f"面试官编号 {item.interviewer_id}",
                now,
                interviewer_minimum_minutes,
            )
            for item in payload.interviewers
        }
        slot_count = self.repository.replace_future_availability(
            candidate_slots=candidate_slots,
            interviewer_slots=interviewer_slots,
            now=now,
        )
        return AvailabilityBatchResult(
            candidate_count=len(candidate_slots),
            interviewer_count=len(interviewer_slots),
            slot_count=slot_count,
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
        if not self.repository.participants_have_available_slot(
            candidate_id=candidate.id,
            interviewer_id=payload.interviewer_id,
            start_at=payload.start_at,
            end_at=payload.end_at,
        ):
            raise TalentFlowError("RESOURCE_UNAVAILABLE", "候选人或面试官在该时间段不可用，请重新生成排期建议。")
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
    def _ensure_unique_resource_ids(resource_ids: list[int], resource_name: str) -> None:
        if len(resource_ids) != len(set(resource_ids)):
            raise TalentFlowError("DUPLICATE_AVAILABILITY_RESOURCE", f"同一{resource_name}不能重复提交空闲时间。")

    @staticmethod
    def _validate_availability_slots(
        slots: list[AvailabilitySlotWrite],
        resource_name: str,
        now: datetime,
        minimum_minutes: int,
    ) -> list[tuple[datetime, datetime]]:
        if not slots:
            raise TalentFlowError("AVAILABILITY_SLOT_REQUIRED", f"{resource_name}至少需要一组空闲时间。")

        normalized: list[tuple[datetime, datetime]] = []
        for slot in slots:
            if slot.start_at.tzinfo is None or slot.start_at.utcoffset() is None \
                    or slot.end_at.tzinfo is None or slot.end_at.utcoffset() is None:
                raise TalentFlowError("INVALID_AVAILABILITY_TIME", f"{resource_name}的空闲时间必须包含时区。")
            start_at = slot.start_at.astimezone(timezone.utc)
            end_at = slot.end_at.astimezone(timezone.utc)
            if start_at <= now:
                raise TalentFlowError("AVAILABILITY_IN_PAST", f"{resource_name}的空闲时间必须位于未来。")
            if end_at <= start_at:
                raise TalentFlowError("INVALID_AVAILABILITY_TIME", f"{resource_name}的结束时间必须晚于开始时间。")
            if (end_at - start_at).total_seconds() < minimum_minutes * 60:
                raise TalentFlowError(
                    "AVAILABILITY_TOO_SHORT",
                    f"{resource_name}的每组空闲时间不得少于 {minimum_minutes} 分钟。",
                )
            normalized.append((start_at, end_at))

        normalized.sort(key=lambda item: item[0])
        for previous, current in zip(normalized, normalized[1:]):
            if current[0] < previous[1]:
                raise TalentFlowError("AVAILABILITY_OVERLAP", f"{resource_name}的空闲时间不能重叠。")
        return normalized

    @staticmethod
    def _slot_rows(slots: list[Any]) -> list[dict[str, str]]:
        return [{"start": slot.start_at.isoformat(), "end": slot.end_at.isoformat()} for slot in slots]

    @staticmethod
    def _load_schedule_interview() -> Any | None:
        return load_human_only_function(INTERVIEW_SCHEDULER_CONTRACT)
