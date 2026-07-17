from datetime import datetime, timedelta

from app.human_only.interview_scheduler import schedule_interview


def test_recommends_slot_when_availability_overlaps() -> None:
    result = schedule_interview(
        {
            "candidate": {
                "available_slots": [{"start": "2026-07-08T10:00:00", "end": "2026-07-08T12:00:00"}]
            },
            "interviewers": [
                {
                    "interviewer_id": 1,
                    "employee_name": "王刚",
                    "available_slots": [{"start": "2026-07-08T09:00:00", "end": "2026-07-08T11:00:00"}],
                }
            ],
            "meeting_rooms": [
                {
                    "meeting_room_id": 1,
                    "room_name": "会议室 A",
                    "available_slots": [{"start": "2026-07-08T10:00:00", "end": "2026-07-08T11:30:00"}],
                }
            ],
            "duration_minutes": 60,
        }
    )

    assert result["status"] == "success"
    assert result["best_slot"]["start"] == "2026-07-08T10:00"
    assert result["recommended_slots"]


def test_conflicting_existing_event_is_excluded() -> None:
    result = schedule_interview(
        {
            "candidate": {
                "candidate_id": 1,
                "available_slots": [{"start": "2026-07-08T10:00:00", "end": "2026-07-08T11:00:00"}]
            },
            "interviewers": [
                {
                    "interviewer_id": 1,
                    "available_slots": [{"start": "2026-07-08T10:00:00", "end": "2026-07-08T11:00:00"}],
                }
            ],
            "existing_interviews": [
                {
                    "start": "2026-07-08T10:15:00",
                    "end": "2026-07-08T10:45:00",
                    "interviewer_id": 1
                }
            ],
            "duration_minutes": 30,
        }
    )

    assert result["status"] == "no_available_slot"
    assert result["conflicts"]


def test_search_continues_after_window_start_conflict() -> None:
    result = schedule_interview(
        {
            "candidate": {
                "candidate_id": 1,
                "available_slots": [
                    {"start": "2026-07-18T22:12:00+08:00", "end": "2026-07-19T22:12:00+08:00"}
                ],
            },
            "interviewers": [
                {
                    "interviewer_id": 1,
                    "employee_name": "王刚",
                    "available_slots": [
                        {"start": "2026-07-18T22:12:00+08:00", "end": "2026-07-19T22:12:00+08:00"}
                    ],
                }
            ],
            "meeting_rooms": [
                {
                    "meeting_room_id": 1,
                    "room_name": "会议室 A",
                    "available_slots": [
                        {"start": "2026-07-18T22:12:00+08:00", "end": "2026-07-19T22:12:00+08:00"}
                    ],
                }
            ],
            "existing_interviews": [
                {
                    "start": "2026-07-18T22:12:00+08:00",
                    "end": "2026-07-18T22:57:00+08:00",
                    "interviewer_id": 1,
                }
            ],
            "duration_minutes": 45,
        }
    )

    assert result["status"] == "success"
    recommended_start = datetime.fromisoformat(result["recommended_time"]["start"])
    recommended_end = datetime.fromisoformat(result["recommended_time"]["end"])
    conflict_end = datetime.fromisoformat("2026-07-18T22:57:00+08:00")
    assert recommended_start >= conflict_end
    assert recommended_end - recommended_start == timedelta(minutes=45)
    assert all(slot["start"] != "2026-07-18T22:12+08:00" for slot in result["recommended_slots"])


def test_no_overlap_returns_no_available_slot() -> None:
    result = schedule_interview(
        {
            "candidate": {
                "available_slots": [{"start": "2026-07-08T10:00:00", "end": "2026-07-08T11:00:00"}]
            },
            "interviewers": [
                {
                    "interviewer_id": 1,
                    "available_slots": [{"start": "2026-07-08T13:00:00", "end": "2026-07-08T14:00:00"}],
                }
            ],
            "duration_minutes": 60,
        }
    )

    assert result["status"] == "no_available_slot"


def test_missing_schedule_data_returns_invalid_input() -> None:
    result = schedule_interview({"candidate": {"available_slots": []}, "interviewers": []})

    assert result["status"] == "invalid_input"
