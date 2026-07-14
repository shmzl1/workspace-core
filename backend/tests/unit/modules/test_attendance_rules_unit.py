from datetime import datetime, time
from types import SimpleNamespace

import pytest

from app.modules.attendance.rules import calculate_check_in_status, calculate_check_out_status


def work_calendar(*, is_workday: bool = True, grace: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        is_workday=is_workday,
        standard_check_in_time=time(9, 0),
        standard_check_out_time=time(18, 0),
        late_grace_minutes=grace,
    )


@pytest.mark.parametrize(
    ("checked_at", "calendar", "expected"),
    [
        (datetime(2026, 7, 14, 9, 0), None, ("NORMAL", 0)),
        (datetime(2026, 7, 14, 9, 1), None, ("LATE", 1)),
        (datetime(2026, 7, 14, 9, 10), work_calendar(grace=10), ("NORMAL", 0)),
        (datetime(2026, 7, 14, 9, 11), work_calendar(grace=10), ("LATE", 11)),
        (datetime(2026, 7, 14, 0, 0), work_calendar(), ("NORMAL", 0)),
        (datetime(2026, 7, 14, 23, 59), work_calendar(is_workday=False), ("NORMAL", 0)),
    ],
)
def test_calculate_check_in_status_boundaries(checked_at, calendar, expected) -> None:
    assert calculate_check_in_status(checked_at, calendar) == expected


@pytest.mark.parametrize(
    ("checked_at", "current_status", "calendar", "expected"),
    [
        (datetime(2026, 7, 14, 17, 30), "NORMAL", None, ("EARLY_LEAVE", 30)),
        (datetime(2026, 7, 14, 17, 30), "LATE", None, ("LATE", 30)),
        (datetime(2026, 7, 14, 17, 59), "NORMAL", work_calendar(), ("EARLY_LEAVE", 1)),
        (datetime(2026, 7, 14, 18, 0), "NORMAL", None, ("NORMAL", 0)),
        (datetime(2026, 7, 14, 23, 59), "NORMAL", None, ("NORMAL", 0)),
        (datetime(2026, 7, 14, 0, 0), "NORMAL", None, ("EARLY_LEAVE", 1080)),
        (datetime(2026, 7, 14, 0, 0), "LATE", work_calendar(is_workday=False), ("LATE", 0)),
    ],
)
def test_calculate_check_out_status_boundaries(checked_at, current_status, calendar, expected) -> None:
    assert calculate_check_out_status(checked_at, current_status, calendar) == expected
