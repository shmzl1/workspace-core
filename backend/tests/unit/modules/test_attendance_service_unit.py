from datetime import date, datetime, time
from types import SimpleNamespace

import pytest

from app.core.exceptions import TalentFlowError
from app.modules.attendance.service import AttendanceService


class FakeAttendanceRepository:
    def __init__(self) -> None:
        self.session = object()
        self.records: dict[tuple[int, date], object] = {}

    def get_record(self, employee_id: int, attendance_date: date):
        return self.records.get((employee_id, attendance_date))

    def save_record(self, record):
        self.records[(record.employee_id, record.attendance_date)] = record
        return record

    def get_records_by_range(self, employee_id: int, start_date: date, end_date: date):
        return [
            record
            for (record_employee_id, record_date), record in self.records.items()
            if record_employee_id == employee_id and start_date <= record_date <= end_date
        ]


class FakeCalendarRepository:
    def __init__(self, calendar_by_date: dict[date, object | None]) -> None:
        self.calendar_by_date = calendar_by_date

    def get_calendar_by_date(self, attendance_date: date):
        return self.calendar_by_date.get(attendance_date)


def workday(*, is_workday: bool = True, grace: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        is_workday=is_workday,
        standard_check_in_time=time(9, 0),
        standard_check_out_time=time(18, 0),
        late_grace_minutes=grace,
    )


def service_with_calendar(calendar_by_date: dict[date, object | None]) -> tuple[AttendanceService, FakeAttendanceRepository]:
    repository = FakeAttendanceRepository()
    service = AttendanceService(repository)
    service.calendar_repo = FakeCalendarRepository(calendar_by_date)
    return service, repository


def test_check_in_and_out_preserve_late_status_and_early_leave_minutes() -> None:
    attendance_date = date(2026, 7, 14)
    service, _ = service_with_calendar({attendance_date: workday(grace=5)})

    checked_in = service.check_in(7, datetime(2026, 7, 14, 9, 6), source="MINIPROGRAM")
    checked_out = service.check_out(7, datetime(2026, 7, 14, 17, 0), source="MINIPROGRAM")

    assert checked_in.status == "LATE"
    assert checked_in.late_minutes == 6
    assert checked_out.status == "LATE"
    assert checked_out.early_leave_minutes == 60
    assert checked_out.source == "MINIPROGRAM"


@pytest.mark.parametrize(
    ("calendar", "expected_code"),
    [
        (None, "WORK_CALENDAR_NOT_FOUND"),
        (workday(is_workday=False), "NOT_A_WORKDAY"),
    ],
)
def test_check_in_rejects_missing_calendar_and_non_workdays(calendar, expected_code: str) -> None:
    attendance_date = date(2026, 7, 14)
    service, _ = service_with_calendar({attendance_date: calendar})

    with pytest.raises(TalentFlowError) as error:
        service.check_in(7, datetime(2026, 7, 14, 9, 0))

    assert error.value.code == expected_code


def test_check_out_requires_check_in_and_prevents_duplicate_check_out() -> None:
    attendance_date = date(2026, 7, 14)
    service, _ = service_with_calendar({attendance_date: workday()})

    with pytest.raises(TalentFlowError) as missing_check_in:
        service.check_out(7, datetime(2026, 7, 14, 18, 0))
    assert missing_check_in.value.code == "CHECK_IN_REQUIRED"

    service.check_in(7, datetime(2026, 7, 14, 9, 0))
    service.check_out(7, datetime(2026, 7, 14, 18, 0))
    with pytest.raises(TalentFlowError) as duplicate:
        service.check_out(7, datetime(2026, 7, 14, 18, 1))
    assert duplicate.value.code == "DUPLICATE_CHECK_OUT"


def test_weekly_summary_marks_past_missing_workdays_absent_only() -> None:
    monday = date(2026, 7, 13)
    service, repository = service_with_calendar({})
    repository.records[(7, monday)] = SimpleNamespace(employee_id=7, attendance_date=monday, status="NORMAL")

    summary = service.get_weekly_summary(7, date(2026, 7, 15))

    assert [record.attendance_date for record in summary] == [date(2026, 7, 13 + offset) for offset in range(7)]
    assert [record.status for record in summary] == ["NORMAL", "ABSENT", "NORMAL", "NORMAL", "NORMAL", "NORMAL", "NORMAL"]
