from datetime import datetime
from types import SimpleNamespace

import pytest

from app.core.exceptions import TalentFlowError
from app.modules.interview.schemas import ConfirmScheduleRequest, SchedulePreviewRequest
from app.modules.interview.service import InterviewService


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
