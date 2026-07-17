import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.interview_availability_backfill import backfill_candidate_availability


NOW = datetime(2099, 1, 4, 8, tzinfo=timezone.utc)


class _ScalarResult:
    def __init__(self, values: list) -> None:
        self._values = values

    def all(self) -> list:
        return self._values


class _FakeSession:
    def __init__(self, scalar_results: list[list]) -> None:
        self._scalar_results = iter(scalar_results)
        self.added: list = []

    def scalars(self, _statement) -> _ScalarResult:
        return _ScalarResult(next(self._scalar_results))

    def add_all(self, values: list) -> None:
        self.added.extend(values)


def _resource_slot(resource: str, day_offset: int) -> SimpleNamespace:
    start_at = NOW + timedelta(days=day_offset, hours=1)
    values = {
        "start_at": start_at,
        "end_at": start_at + timedelta(hours=3),
        "interviewer_id": 41 if resource == "INTERVIEWER" else None,
        "meeting_room_id": 51 if resource == "ROOM" else None,
    }
    return SimpleNamespace(**values)


def _backfill_session(
    *,
    candidate_ids: list[int],
    existing_valid_ids: list[int],
    existing_slots: list | None = None,
) -> _FakeSession:
    interviewer_slots = [_resource_slot("INTERVIEWER", offset) for offset in (1, 2, 3, 4)]
    room_slots = [_resource_slot("ROOM", offset) for offset in (1, 2, 3, 4)]
    results = [candidate_ids, existing_valid_ids]
    if len(existing_valid_ids) < len(set(candidate_ids)):
        results.extend([interviewer_slots, room_slots, [], existing_slots or []])
    return _FakeSession(results)


def test_backfill_first_run_creates_three_valid_slots_per_missing_candidate() -> None:
    session = _backfill_session(candidate_ids=[101, 205], existing_valid_ids=[])

    stats = backfill_candidate_availability(session, now=NOW)

    assert stats.created_slots == 6
    assert stats.backfilled_candidates == 2
    assert {slot.candidate_id for slot in session.added} == {101, 205}
    assert all(slot.resource_type == "CANDIDATE" for slot in session.added)
    assert all(slot.interviewer_id is None and slot.meeting_room_id is None for slot in session.added)
    assert all(slot.is_available and slot.end_at > slot.start_at for slot in session.added)
    assert all(slot.end_at - slot.start_at >= timedelta(minutes=60) for slot in session.added)


def test_backfill_second_run_is_idempotent() -> None:
    session = _backfill_session(candidate_ids=[101, 205], existing_valid_ids=[101, 205])

    stats = backfill_candidate_availability(session, now=NOW)

    assert stats.created_slots == 0
    assert stats.existing_valid_candidates == 2
    assert session.added == []


def test_backfill_preserves_candidate_with_manual_availability() -> None:
    session = _backfill_session(candidate_ids=[101, 205], existing_valid_ids=[101])

    stats = backfill_candidate_availability(session, now=NOW)

    assert stats.created_slots == 3
    assert {slot.candidate_id for slot in session.added} == {205}


def test_backfill_does_not_reactivate_disabled_duplicate_slot() -> None:
    disabled = SimpleNamespace(
        candidate_id=205,
        start_at=NOW + timedelta(days=1, hours=1),
        end_at=NOW + timedelta(days=1, hours=4),
        is_available=False,
    )
    session = _backfill_session(
        candidate_ids=[205],
        existing_valid_ids=[],
        existing_slots=[disabled],
    )

    stats = backfill_candidate_availability(session, now=NOW)

    assert stats.created_slots == 3
    assert disabled.is_available is False
    assert all(
        (slot.start_at, slot.end_at) != (disabled.start_at, disabled.end_at)
        for slot in session.added
    )


def test_backfill_stops_when_interviewer_availability_is_missing() -> None:
    session = _FakeSession([[101], [], []])

    with pytest.raises(RuntimeError, match="面试官"):
        backfill_candidate_availability(session, now=NOW)

    assert session.added == []
