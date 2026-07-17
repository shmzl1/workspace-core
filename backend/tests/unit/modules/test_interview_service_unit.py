from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.core.exceptions import TalentFlowError
from app.modules.interview.schemas import ConfirmScheduleRequest, SchedulePreviewRequest
from app.modules.interview.service import InterviewService


def _slot(start_hour: int = 9, end_hour: int = 12) -> SimpleNamespace:
    return SimpleNamespace(
        start_at=datetime(2099, 1, 5, start_hour, tzinfo=timezone.utc),
        end_at=datetime(2099, 1, 5, end_hour, tzinfo=timezone.utc),
    )


def _preview_repository(
    *,
    candidate_slots: list[SimpleNamespace] | None = None,
    interviewer_slots: list[SimpleNamespace] | None = None,
    room_slots: list[SimpleNamespace] | None = None,
) -> SimpleNamespace:
    application = SimpleNamespace(id=9)
    candidate = SimpleNamespace(id=17, full_name="候选人")
    job = SimpleNamespace(id=3)
    interviewer = SimpleNamespace(id=4, specialties=["Python"])
    employee = SimpleNamespace(full_name="面试官")
    room = SimpleNamespace(id=6, name="会议室")
    return SimpleNamespace(
        get_application_detail=lambda _application_id: (application, candidate, job),
        list_candidate_slots=lambda _candidate_id, *, ends_after: candidate_slots or [],
        list_interviewers_with_employees=lambda: [(interviewer, employee)],
        list_interviewer_slots=lambda _interviewer_id, *, ends_after: interviewer_slots or [],
        list_meeting_rooms=lambda: [room],
        list_room_slots=lambda _room_id, *, ends_after: room_slots or [],
        list_scheduled_interviews_with_applications=lambda: [],
    )


def test_preview_returns_human_only_not_ready_response_without_repository_access(monkeypatch: pytest.MonkeyPatch) -> None:
    service = InterviewService(SimpleNamespace())
    monkeypatch.setattr(InterviewService, "_load_schedule_interview", staticmethod(lambda: None))

    response = service.preview_schedule(SchedulePreviewRequest(application_id=9))

    assert response.status == "algorithm_not_ready"
    assert response.expected_function == "schedule_interview"
    assert response.requires_human_only is True


def test_confirm_schedule_rejects_non_positive_time_range_before_querying_repository() -> None:
    service = InterviewService(SimpleNamespace())
    payload = ConfirmScheduleRequest(
        application_id=9,
        interviewer_id=3,
        meeting_room_id=2,
        start_at=datetime(2026, 7, 14, 10, 0),
        end_at=datetime(2026, 7, 14, 10, 0),
    )

    with pytest.raises(TalentFlowError) as error:
        service.confirm_schedule(payload)

    assert error.value.code == "INVALID_INTERVIEW_TIME"


def test_preview_reports_missing_candidate_availability(monkeypatch: pytest.MonkeyPatch) -> None:
    service = InterviewService(_preview_repository(candidate_slots=[]))
    monkeypatch.setattr(InterviewService, "_load_schedule_interview", staticmethod(lambda: lambda _payload: {}))

    response = service.preview_schedule(SchedulePreviewRequest(application_id=9))

    assert response.status == "candidate_availability_missing"
    assert "候选人" in response.message


def test_preview_reports_missing_interviewer_availability(monkeypatch: pytest.MonkeyPatch) -> None:
    service = InterviewService(_preview_repository(candidate_slots=[_slot()], interviewer_slots=[]))
    monkeypatch.setattr(InterviewService, "_load_schedule_interview", staticmethod(lambda: lambda _payload: {}))

    response = service.preview_schedule(SchedulePreviewRequest(application_id=9))

    assert response.status == "interviewer_availability_missing"
    assert "面试官" in response.message


def test_preview_reports_missing_room_availability(monkeypatch: pytest.MonkeyPatch) -> None:
    service = InterviewService(_preview_repository(
        candidate_slots=[_slot()],
        interviewer_slots=[_slot()],
        room_slots=[],
    ))
    monkeypatch.setattr(InterviewService, "_load_schedule_interview", staticmethod(lambda: lambda _payload: {}))

    response = service.preview_schedule(SchedulePreviewRequest(application_id=9))

    assert response.status == "room_availability_missing"
    assert "会议室" in response.message


def test_preview_generates_recommendation_when_all_resources_have_availability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_payload: dict = {}

    def schedule(payload: dict) -> dict:
        captured_payload.update(payload)
        return {
            "status": "success",
            "message": "已生成智能排期建议。",
            "recommended_time": {
                "start": "2099-01-05T09:00+00:00",
                "end": "2099-01-05T10:00+00:00",
            },
            "recommended_interviewer_id": 4,
            "recommended_room_id": 6,
            "recommendation_reason": "三类资源存在 60 分钟交集。",
            "best_slot": {"conflict": False},
            "conflict_explanation": {
                "conflicts": [{"type": "event_conflict", "message": "另一个候选时段已占用。"}],
            },
        }

    service = InterviewService(_preview_repository(
        candidate_slots=[_slot()],
        interviewer_slots=[_slot()],
        room_slots=[_slot()],
    ))
    monkeypatch.setattr(InterviewService, "_load_schedule_interview", staticmethod(lambda: schedule))

    response = service.preview_schedule(SchedulePreviewRequest(application_id=9, duration_minutes=60))

    assert response.status == "success"
    assert response.recommended_time == {
        "start": "2099-01-05T09:00+00:00",
        "end": "2099-01-05T10:00+00:00",
    }
    assert captured_payload["candidate"]["available_slots"]
    assert captured_payload["interviewers"][0]["available_slots"]
    assert captured_payload["meeting_rooms"][0]["available_slots"]
    assert response.conflict_explanation["recommended_slot_conflict"] is False
    assert response.conflict_explanation["conflicts"]
