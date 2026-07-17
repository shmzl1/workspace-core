from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.core.exceptions import TalentFlowError
from app.modules.interview.repository import InterviewRepository
from app.modules.interview.schemas import AvailabilityBatchWrite, ConfirmScheduleRequest, SchedulePreviewRequest
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
    has_rooms: bool = True,
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
        list_meeting_rooms=lambda: [room] if has_rooms else [],
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


def test_confirm_schedule_treats_enabled_room_as_available_without_room_slot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application = SimpleNamespace(id=9, current_stage="INTERVIEW_PENDING")
    candidate = SimpleNamespace(id=17)
    saved_interview = SimpleNamespace(
        id=31,
        application_id=9,
        interviewer_id=5,
        meeting_room_id=6,
        start_at=datetime(2099, 1, 5, 9, tzinfo=timezone.utc),
        end_at=datetime(2099, 1, 5, 10, tzinfo=timezone.utc),
        status="SCHEDULED",
        conflict_explanation={},
        created_by_user_id=None,
    )
    repository = SimpleNamespace(
        get_application_detail=lambda _application_id: (application, candidate, SimpleNamespace(id=3)),
        get_interviewer_with_employee=lambda _interviewer_id: (SimpleNamespace(id=5), None),
        get_meeting_room=lambda _room_id: SimpleNamespace(id=6),
        participants_have_available_slot=lambda **_values: True,
        find_conflicts=lambda **_values: [],
        save_interview=lambda **_values: saved_interview,
    )
    service = InterviewService(repository)
    monkeypatch.setattr(service, "_advance_for_scheduled_interview", lambda *_args: None)

    response = service.confirm_schedule(ConfirmScheduleRequest(
        application_id=9,
        interviewer_id=5,
        meeting_room_id=6,
        start_at=saved_interview.start_at,
        end_at=saved_interview.end_at,
    ))

    assert response.id == 31
    assert response.meeting_room_id == 6


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


def test_preview_reports_missing_room_resources(monkeypatch: pytest.MonkeyPatch) -> None:
    service = InterviewService(_preview_repository(
        candidate_slots=[_slot()],
        interviewer_slots=[_slot()],
        has_rooms=False,
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
    assert captured_payload["meeting_rooms"][0]["available_slots"] == captured_payload["candidate"]["available_slots"]
    assert response.conflict_explanation["recommended_slot_conflict"] is False
    assert response.conflict_explanation["conflicts"]


def test_preview_passes_only_selected_interviewers_to_scheduler(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_payload: dict = {}
    application = SimpleNamespace(id=9)
    candidate = SimpleNamespace(id=17, full_name="候选人")
    interviewers = [
        (SimpleNamespace(id=4, specialties=["Python"]), SimpleNamespace(full_name="甲面试官")),
        (SimpleNamespace(id=5, specialties=["Vue"]), SimpleNamespace(full_name="乙面试官")),
    ]
    repository = SimpleNamespace(
        get_application_detail=lambda _application_id: (application, candidate, SimpleNamespace(id=3)),
        list_candidate_slots=lambda _candidate_id, *, ends_after: [_slot()],
        list_interviewers_with_employees=lambda: interviewers,
        list_interviewer_slots=lambda _interviewer_id, *, ends_after: [_slot()],
        list_meeting_rooms=lambda: [SimpleNamespace(id=6, name="会议室")],
        list_scheduled_interviews_with_applications=lambda: [],
    )

    def schedule(payload: dict) -> dict:
        captured_payload.update(payload)
        return {
            "status": "success",
            "recommended_time": {"start": "2099-01-05T09:00+00:00", "end": "2099-01-05T10:00+00:00"},
            "recommended_interviewer_id": 5,
            "recommended_room_id": 6,
        }

    monkeypatch.setattr(InterviewService, "_load_schedule_interview", staticmethod(lambda: schedule))

    InterviewService(repository).preview_schedule(SchedulePreviewRequest(application_id=9, interviewer_ids=[5]))

    assert [item["interviewer_id"] for item in captured_payload["interviewers"]] == [5]


def test_preview_rejects_empty_selected_interviewer_list() -> None:
    service = InterviewService(SimpleNamespace())

    with pytest.raises(TalentFlowError) as error:
        service.preview_schedule(SchedulePreviewRequest(application_id=9, interviewer_ids=[]))

    assert error.value.code == "INTERVIEWER_REQUIRED"


def test_preview_rejects_missing_or_inactive_selected_interviewer(monkeypatch: pytest.MonkeyPatch) -> None:
    service = InterviewService(_preview_repository(candidate_slots=[_slot()]))
    monkeypatch.setattr(InterviewService, "_load_schedule_interview", staticmethod(lambda: lambda _payload: {}))

    with pytest.raises(TalentFlowError) as error:
        service.preview_schedule(SchedulePreviewRequest(application_id=9, interviewer_ids=[99]))

    assert error.value.code == "INTERVIEWER_NOT_FOUND"


def test_save_availability_saves_candidate_and_interviewer_slots() -> None:
    captured: dict = {}
    repository = SimpleNamespace(
        get_candidate=lambda candidate_id: SimpleNamespace(id=candidate_id) if candidate_id == 17 else None,
        get_interviewer_with_employee=lambda interviewer_id: (SimpleNamespace(id=interviewer_id), None)
        if interviewer_id == 5 else None,
        replace_future_availability=lambda **values: captured.update(values) or 3,
    )
    payload = AvailabilityBatchWrite.model_validate({
        "candidates": [{
            "candidate_id": 17,
            "duration_minutes": 90,
            "slots": [
                {"start_at": "2099-01-05T09:00:00+08:00", "end_at": "2099-01-05T11:00:00+08:00"},
                {"start_at": "2099-01-06T09:00:00+08:00", "end_at": "2099-01-06T11:00:00+08:00"},
            ],
        }],
        "interviewers": [{
            "interviewer_id": 5,
            "slots": [{"start_at": "2099-01-05T10:00:00+08:00", "end_at": "2099-01-05T12:00:00+08:00"}],
        }],
    })

    result = InterviewService(repository).save_availability(payload)

    assert result.candidate_count == 1
    assert result.interviewer_count == 1
    assert result.slot_count == 3
    assert len(captured["candidate_slots"][17]) == 2
    assert len(captured["interviewer_slots"][5]) == 1
    assert captured["candidate_slots"][17][0][0].tzinfo is timezone.utc


@pytest.mark.parametrize(
    ("slots", "expected_code"),
    [
        (
            [{"start_at": "2020-01-05T09:00:00+08:00", "end_at": "2020-01-05T11:00:00+08:00"}],
            "AVAILABILITY_IN_PAST",
        ),
        (
            [{"start_at": "2099-01-05T09:00:00+08:00", "end_at": "2099-01-05T09:30:00+08:00"}],
            "AVAILABILITY_TOO_SHORT",
        ),
        (
            [
                {"start_at": "2099-01-05T09:00:00+08:00", "end_at": "2099-01-05T11:00:00+08:00"},
                {"start_at": "2099-01-05T10:00:00+08:00", "end_at": "2099-01-05T12:00:00+08:00"},
            ],
            "AVAILABILITY_OVERLAP",
        ),
    ],
)
def test_save_availability_rejects_invalid_time_ranges(slots: list[dict], expected_code: str) -> None:
    repository = SimpleNamespace(
        get_candidate=lambda _candidate_id: SimpleNamespace(id=17),
        get_interviewer_with_employee=lambda _interviewer_id: None,
    )
    payload = AvailabilityBatchWrite.model_validate({
        "candidates": [{"candidate_id": 17, "slots": slots}],
        "interviewers": [],
    })

    with pytest.raises(TalentFlowError) as error:
        InterviewService(repository).save_availability(payload)

    assert error.value.code == expected_code


def test_save_availability_uses_candidate_duration_as_minimum_slot_length() -> None:
    repository = SimpleNamespace(
        get_candidate=lambda _candidate_id: SimpleNamespace(id=17),
        get_interviewer_with_employee=lambda _interviewer_id: None,
    )
    payload = AvailabilityBatchWrite.model_validate({
        "candidates": [{
            "candidate_id": 17,
            "duration_minutes": 90,
            "slots": [{"start_at": "2099-01-05T09:00:00+08:00", "end_at": "2099-01-05T10:00:00+08:00"}],
        }],
        "interviewers": [],
    })

    with pytest.raises(TalentFlowError) as error:
        InterviewService(repository).save_availability(payload)

    assert error.value.code == "AVAILABILITY_TOO_SHORT"
    assert "90 分钟" in error.value.message


def test_replace_future_availability_keeps_history_and_commits_once() -> None:
    class FakeSession:
        def __init__(self) -> None:
            self.statements: list = []
            self.added: list = []
            self.commit_count = 0
            self.rollback_count = 0

        def execute(self, statement) -> None:
            self.statements.append(statement)

        def add_all(self, values: list) -> None:
            self.added.extend(values)

        def commit(self) -> None:
            self.commit_count += 1

        def rollback(self) -> None:
            self.rollback_count += 1

    session = FakeSession()
    future_start = datetime(2099, 1, 5, 9, tzinfo=timezone.utc)
    future_end = datetime(2099, 1, 5, 11, tzinfo=timezone.utc)

    count = InterviewRepository(session).replace_future_availability(
        candidate_slots={17: [(future_start, future_end)]},
        interviewer_slots={5: [(future_start, future_end)]},
        now=datetime(2099, 1, 1, tzinfo=timezone.utc),
    )

    assert count == 2
    assert session.commit_count == 1
    assert session.rollback_count == 0
    assert len(session.statements) == 2
    assert all("interview_slots.end_at >" in str(statement) for statement in session.statements)
    assert {slot.resource_type for slot in session.added} == {"CANDIDATE", "INTERVIEWER"}
