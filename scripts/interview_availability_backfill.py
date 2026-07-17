"""Non-destructive interview resource and candidate availability backfill."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
for import_path in (ROOT_DIR, BACKEND_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

# Settings load ``.env`` relative to the working directory. Only the standalone
# entry point changes directories; importing this module has no process-wide side effect.
if __name__ == "__main__":
    os.chdir(BACKEND_DIR)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.employee.models import Employee
from app.modules.interview.models import Interview, Interviewer, InterviewSlot, MeetingRoom
from app.modules.recruitment.models import CandidateApplication


DEMO_ROOM_CODE = "DEMO-INTERVIEW-ROOM-001"
DEMO_INTERVIEWER_SPECIALTIES = ["Python", "FastAPI", "系统设计", "项目经验", "沟通表达"]


@dataclass(frozen=True)
class SharedAvailabilityWindow:
    start_at: datetime
    end_at: datetime
    interviewer_id: int
    meeting_room_id: int


@dataclass(frozen=True)
class CandidateAvailabilityBackfillStats:
    total_candidates: int
    existing_valid_candidates: int
    backfilled_candidates: int
    created_slots: int
    skipped_candidates: int


@dataclass(frozen=True)
class InterviewResourceAvailabilityStats:
    interviewer_id: int
    interviewer_name: str
    meeting_room_id: int
    meeting_room_name: str
    created_interviewers: int
    created_rooms: int
    created_interviewer_slots: int
    created_room_slots: int
    covered_candidates: int


def find_shared_availability_windows(
    interviewer_slots: Iterable[Any],
    room_slots: Iterable[Any],
    scheduled_interviews: Iterable[Any],
    *,
    now: datetime,
    duration_minutes: int = 60,
) -> list[SharedAvailabilityWindow]:
    """Return future interviewer-room intersections that are not already occupied."""

    minimum_duration = timedelta(minutes=duration_minutes)
    interviews = list(scheduled_interviews)
    windows: dict[tuple[datetime, datetime], SharedAvailabilityWindow] = {}
    for interviewer_slot in interviewer_slots:
        for room_slot in room_slots:
            start_at = max(interviewer_slot.start_at, room_slot.start_at, now)
            end_at = min(interviewer_slot.end_at, room_slot.end_at)
            if end_at - start_at < minimum_duration:
                continue
            if any(
                start_at < interview.end_at
                and end_at > interview.start_at
                and (
                    interview.interviewer_id == interviewer_slot.interviewer_id
                    or interview.meeting_room_id == room_slot.meeting_room_id
                )
                for interview in interviews
            ):
                continue
            key = (start_at, end_at)
            windows.setdefault(
                key,
                SharedAvailabilityWindow(
                    start_at=start_at,
                    end_at=end_at,
                    interviewer_id=interviewer_slot.interviewer_id,
                    meeting_room_id=room_slot.meeting_room_id,
                ),
            )
    return sorted(windows.values(), key=lambda item: (item.start_at, item.end_at))


def backfill_candidate_availability(
    session: Session,
    *,
    now: datetime | None = None,
    slots_per_candidate: int = 3,
    minimum_duration_minutes: int = 60,
) -> CandidateAvailabilityBackfillStats:
    """Add demo availability only for applicants without a valid future slot.

    The caller owns the transaction. Existing slots are never updated or deleted.
    """

    current_time = now or datetime.now(timezone.utc)
    _validate_aware_datetime(current_time)
    if slots_per_candidate < 1:
        raise ValueError("slots_per_candidate must be positive")
    if minimum_duration_minutes < 1:
        raise ValueError("minimum_duration_minutes must be positive")
    minimum_duration = timedelta(minutes=minimum_duration_minutes)

    candidate_ids = sorted(set(session.scalars(
        select(CandidateApplication.candidate_id).distinct()
    ).all()))
    if not candidate_ids:
        return CandidateAvailabilityBackfillStats(0, 0, 0, 0, 0)

    existing_valid_candidate_ids = set(session.scalars(
        select(InterviewSlot.candidate_id).where(
            InterviewSlot.resource_type == "CANDIDATE",
            InterviewSlot.candidate_id.in_(candidate_ids),
            InterviewSlot.is_available.is_(True),
            InterviewSlot.end_at > current_time,
            InterviewSlot.end_at - InterviewSlot.start_at >= minimum_duration,
        ).distinct()
    ).all())
    missing_candidate_ids = [
        candidate_id for candidate_id in candidate_ids
        if candidate_id not in existing_valid_candidate_ids
    ]
    if not missing_candidate_ids:
        return CandidateAvailabilityBackfillStats(
            total_candidates=len(candidate_ids),
            existing_valid_candidates=len(existing_valid_candidate_ids),
            backfilled_candidates=0,
            created_slots=0,
            skipped_candidates=len(existing_valid_candidate_ids),
        )

    interviewer_slots = session.scalars(
        select(InterviewSlot)
        .join(Interviewer, Interviewer.id == InterviewSlot.interviewer_id)
        .where(
            InterviewSlot.resource_type == "INTERVIEWER",
            InterviewSlot.is_available.is_(True),
            InterviewSlot.end_at > current_time,
            Interviewer.is_active.is_(True),
        )
        .order_by(InterviewSlot.start_at)
    ).all()
    if not interviewer_slots:
        raise RuntimeError("没有启用面试官的有效未来可用时间，候选人可用时间补全已停止。")

    room_slots = session.scalars(
        select(InterviewSlot)
        .join(MeetingRoom, MeetingRoom.id == InterviewSlot.meeting_room_id)
        .where(
            InterviewSlot.resource_type == "ROOM",
            InterviewSlot.is_available.is_(True),
            InterviewSlot.end_at > current_time,
            MeetingRoom.is_active.is_(True),
        )
        .order_by(InterviewSlot.start_at)
    ).all()
    if not room_slots:
        raise RuntimeError("没有启用会议室的有效未来可用时间，候选人可用时间补全已停止。")

    scheduled_interviews = session.scalars(
        select(Interview).where(
            Interview.status == "SCHEDULED",
            Interview.end_at > current_time,
        )
    ).all()
    shared_windows = find_shared_availability_windows(
        interviewer_slots,
        room_slots,
        scheduled_interviews,
        now=current_time,
        duration_minutes=minimum_duration_minutes,
    )
    if not shared_windows:
        raise RuntimeError("面试官和会议室没有满足最小时长且未被占用的未来交集，候选人可用时间补全已停止。")

    existing_candidate_slots = session.scalars(
        select(InterviewSlot).where(
            InterviewSlot.resource_type == "CANDIDATE",
            InterviewSlot.candidate_id.in_(missing_candidate_ids),
        )
    ).all()
    existing_keys = {
        (slot.candidate_id, slot.start_at, slot.end_at)
        for slot in existing_candidate_slots
    }

    new_slots: list[InterviewSlot] = []
    backfilled_candidates = 0
    for candidate_id in missing_candidate_ids:
        candidate_slot_count = 0
        for window in shared_windows:
            key = (candidate_id, window.start_at, window.end_at)
            if key in existing_keys:
                continue
            new_slots.append(InterviewSlot(
                resource_type="CANDIDATE",
                candidate_id=candidate_id,
                interviewer_id=None,
                meeting_room_id=None,
                start_at=window.start_at,
                end_at=window.end_at,
                is_available=True,
                note="demo candidate availability",
            ))
            existing_keys.add(key)
            candidate_slot_count += 1
            if candidate_slot_count >= slots_per_candidate:
                break
        if candidate_slot_count:
            backfilled_candidates += 1

    session.add_all(new_slots)
    unresolved_candidates = len(missing_candidate_ids) - backfilled_candidates
    return CandidateAvailabilityBackfillStats(
        total_candidates=len(candidate_ids),
        existing_valid_candidates=len(existing_valid_candidate_ids),
        backfilled_candidates=backfilled_candidates,
        created_slots=len(new_slots),
        skipped_candidates=len(existing_valid_candidate_ids) + unresolved_candidates,
    )


def ensure_interview_resource_availability(
    session: Session,
    *,
    now: datetime | None = None,
    minimum_duration_minutes: int = 60,
) -> InterviewResourceAvailabilityStats:
    """Ensure demo resources share usable future windows with candidate applicants.

    The operation only inserts missing rows. The caller owns commit and rollback so
    every resource and slot change can be committed as one transaction.
    """

    current_time = now or datetime.now().astimezone()
    _validate_aware_datetime(current_time)
    if minimum_duration_minutes < 1:
        raise ValueError("minimum_duration_minutes must be positive")

    interviewer, employee, created_interviewers = _get_or_create_interviewer(session)
    meeting_room, created_rooms = _get_or_create_meeting_room(session)
    session.flush()

    candidate_ids = sorted(set(session.scalars(
        select(CandidateApplication.candidate_id).distinct()
    ).all()))
    candidate_windows = _list_candidate_windows(
        session,
        candidate_ids=candidate_ids,
        now=current_time,
        minimum_duration_minutes=minimum_duration_minutes,
    )
    if candidate_windows:
        resource_windows = sorted(
            {(start_at, end_at) for _candidate_id, start_at, end_at in candidate_windows}
        )
    else:
        resource_windows = _future_workday_windows(current_time, workday_count=5)

    scheduled_interviews = session.scalars(
        select(Interview).where(
            Interview.status == "SCHEDULED",
            Interview.end_at > current_time,
        )
    ).all()
    conflict_free_windows = [
        window for window in resource_windows
        if not _resource_window_conflicts(
            window,
            scheduled_interviews,
            interviewer_id=interviewer.id,
            meeting_room_id=meeting_room.id,
        )
    ]

    created_interviewer_slots, interviewer_windows = _ensure_resource_slots(
        session,
        resource_type="INTERVIEWER",
        resource_id=interviewer.id,
        windows=conflict_free_windows,
        note="demo auto-generated interviewer availability",
    )
    created_room_slots, room_windows = _ensure_resource_slots(
        session,
        resource_type="ROOM",
        resource_id=meeting_room.id,
        windows=conflict_free_windows,
        note="demo auto-generated room availability",
    )
    shared_resource_windows = interviewer_windows & room_windows
    if candidate_ids and not shared_resource_windows:
        raise RuntimeError("未找到满足最小时长且不与已有面试冲突的公共可用窗口。")

    if candidate_windows:
        covered_candidates = len({
            candidate_id
            for candidate_id, start_at, end_at in candidate_windows
            if (start_at, end_at) in shared_resource_windows
        })
    else:
        session.flush()
        candidate_stats = backfill_candidate_availability(
            session,
            now=current_time,
            minimum_duration_minutes=minimum_duration_minutes,
        )
        covered_candidates = (
            candidate_stats.existing_valid_candidates
            + candidate_stats.backfilled_candidates
        )

    return InterviewResourceAvailabilityStats(
        interviewer_id=interviewer.id,
        interviewer_name=employee.full_name,
        meeting_room_id=meeting_room.id,
        meeting_room_name=meeting_room.name,
        created_interviewers=created_interviewers,
        created_rooms=created_rooms,
        created_interviewer_slots=created_interviewer_slots,
        created_room_slots=created_room_slots,
        covered_candidates=covered_candidates,
    )


def _get_or_create_interviewer(session: Session) -> tuple[Interviewer, Employee, int]:
    interviewer = session.scalar(
        select(Interviewer).where(Interviewer.is_active.is_(True)).order_by(Interviewer.id)
    )
    if interviewer is not None:
        employee = session.get(Employee, interviewer.employee_id)
        if employee is None:
            raise RuntimeError(f"启用面试官（ID={interviewer.id}）未关联有效员工。")
        return interviewer, employee, 0

    employees = list(session.scalars(select(Employee).order_by(Employee.id)).all())
    if not employees:
        raise RuntimeError("数据库中不存在员工，无法创建演示面试官。")

    assigned_employee_ids = set(session.scalars(select(Interviewer.employee_id)).all())
    available_employees = [
        employee for employee in employees
        if employee.id not in assigned_employee_ids
    ]
    if not available_employees:
        raise RuntimeError("现有员工均已关联未启用面试官，无法在不覆盖人工配置的情况下创建演示面试官。")

    employee = min(available_employees, key=_employee_interviewer_priority)
    interviewer = Interviewer(
        employee_id=employee.id,
        specialties=list(DEMO_INTERVIEWER_SPECIALTIES),
        max_interviews_per_day=4,
        is_active=True,
    )
    session.add(interviewer)
    session.flush()
    return interviewer, employee, 1


def _employee_interviewer_priority(employee: Employee) -> tuple[int, int, int]:
    text_value = f"{employee.department} {employee.job_title}".casefold()
    manager_terms = ("经理", "主管", "负责人", "总监", "manager", "lead")
    technical_terms = ("技术", "研发", "开发", "工程", "架构", "算法", "technical", "engineer", "developer")
    if any(term in text_value for term in manager_terms):
        role_priority = 0
    elif any(term in text_value for term in technical_terms):
        role_priority = 1
    else:
        role_priority = 2
    employment_priority = 0 if employee.employment_status == "ACTIVE" else 1
    return employment_priority, role_priority, employee.id


def _get_or_create_meeting_room(session: Session) -> tuple[MeetingRoom, int]:
    meeting_room = session.scalar(
        select(MeetingRoom).where(MeetingRoom.is_active.is_(True)).order_by(MeetingRoom.id)
    )
    if meeting_room is not None:
        return meeting_room, 0

    existing_demo_room = session.scalar(
        select(MeetingRoom).where(MeetingRoom.room_code == DEMO_ROOM_CODE)
    )
    if existing_demo_room is not None:
        raise RuntimeError(
            f"演示会议室 {DEMO_ROOM_CODE} 已存在但未启用，"
            "为避免覆盖人工配置，本次补全未修改其状态。"
        )

    meeting_room = MeetingRoom(
        room_code=DEMO_ROOM_CODE,
        name="智能招聘面试室",
        location="武汉总部演示区",
        capacity=6,
        is_active=True,
    )
    session.add(meeting_room)
    session.flush()
    return meeting_room, 1


def _list_candidate_windows(
    session: Session,
    *,
    candidate_ids: list[int],
    now: datetime,
    minimum_duration_minutes: int,
) -> list[tuple[int, datetime, datetime]]:
    if not candidate_ids:
        return []
    minimum_duration = timedelta(minutes=minimum_duration_minutes)
    slots = session.scalars(
        select(InterviewSlot).where(
            InterviewSlot.resource_type == "CANDIDATE",
            InterviewSlot.candidate_id.is_not(None),
            InterviewSlot.candidate_id.in_(candidate_ids),
            InterviewSlot.is_available.is_(True),
            InterviewSlot.end_at > now,
        ).order_by(InterviewSlot.start_at, InterviewSlot.end_at)
    ).all()
    windows: dict[tuple[int, datetime, datetime], None] = {}
    for slot in slots:
        if slot.end_at - slot.start_at < minimum_duration:
            continue
        windows.setdefault((slot.candidate_id, slot.start_at, slot.end_at), None)
    return list(windows)


def _future_workday_windows(now: datetime, *, workday_count: int) -> list[tuple[datetime, datetime]]:
    windows: list[tuple[datetime, datetime]] = []
    current_day: date = now.date()
    generated_days = 0
    while generated_days < workday_count:
        current_day += timedelta(days=1)
        if current_day.weekday() >= 5:
            continue
        generated_days += 1
        for start_time, end_time in ((time(9), time(12)), (time(14), time(17))):
            windows.append((
                datetime.combine(current_day, start_time, tzinfo=now.tzinfo),
                datetime.combine(current_day, end_time, tzinfo=now.tzinfo),
            ))
    return windows


def _resource_window_conflicts(
    window: tuple[datetime, datetime],
    scheduled_interviews: Iterable[Interview],
    *,
    interviewer_id: int,
    meeting_room_id: int,
) -> bool:
    start_at, end_at = window
    return any(
        start_at < interview.end_at
        and end_at > interview.start_at
        and (
            interview.interviewer_id == interviewer_id
            or interview.meeting_room_id == meeting_room_id
        )
        for interview in scheduled_interviews
    )


def _ensure_resource_slots(
    session: Session,
    *,
    resource_type: str,
    resource_id: int,
    windows: Iterable[tuple[datetime, datetime]],
    note: str,
) -> tuple[int, set[tuple[datetime, datetime]]]:
    if resource_type == "INTERVIEWER":
        resource_clause = InterviewSlot.interviewer_id == resource_id
    elif resource_type == "ROOM":
        resource_clause = InterviewSlot.meeting_room_id == resource_id
    else:
        raise ValueError(f"Unsupported resource type: {resource_type}")

    existing_slots = session.scalars(
        select(InterviewSlot).where(
            InterviewSlot.resource_type == resource_type,
            resource_clause,
        )
    ).all()
    exact_keys = {(slot.start_at, slot.end_at) for slot in existing_slots}
    available_slots = [slot for slot in existing_slots if slot.is_available]
    usable_windows: set[tuple[datetime, datetime]] = set()
    new_slots: list[InterviewSlot] = []

    for start_at, end_at in windows:
        key = (start_at, end_at)
        if any(slot.start_at <= start_at and slot.end_at >= end_at for slot in available_slots):
            usable_windows.add(key)
            continue
        if key in exact_keys:
            continue

        values = {
            "resource_type": resource_type,
            "candidate_id": None,
            "interviewer_id": resource_id if resource_type == "INTERVIEWER" else None,
            "meeting_room_id": resource_id if resource_type == "ROOM" else None,
            "start_at": start_at,
            "end_at": end_at,
            "is_available": True,
            "note": note,
        }
        new_slots.append(InterviewSlot(**values))
        exact_keys.add(key)
        usable_windows.add(key)

    session.add_all(new_slots)
    return len(new_slots), usable_windows


def _validate_aware_datetime(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("now must be timezone-aware")


def _print_stats(stats: InterviewResourceAvailabilityStats) -> None:
    prefix = "[interview-availability]"
    print(f"{prefix} 使用面试官：{stats.interviewer_name}（ID={stats.interviewer_id}）")
    print(f"{prefix} 使用会议室：{stats.meeting_room_name}（ID={stats.meeting_room_id}）")
    print(f"{prefix} 新增面试官：{stats.created_interviewers}")
    print(f"{prefix} 新增会议室：{stats.created_rooms}")
    print(f"{prefix} 新增面试官时段：{stats.created_interviewer_slots}")
    print(f"{prefix} 新增会议室时段：{stats.created_room_slots}")
    print(f"{prefix} 已覆盖候选人：{stats.covered_candidates}")
    if (
        stats.created_interviewers
        or stats.created_rooms
        or stats.created_interviewer_slots
        or stats.created_room_slots
    ):
        print(f"{prefix} 智能排期前置数据已准备完成")
    else:
        print(f"{prefix} 现有数据已经满足智能排期要求")


def main() -> int:
    """Run the standalone backfill against the configured PostgreSQL database."""

    from app.core.database import SessionLocal

    session = SessionLocal()
    try:
        stats = ensure_interview_resource_availability(session)
        session.commit()
    except Exception as exc:
        session.rollback()
        print(f"[interview-availability] 补全失败：{exc}", file=sys.stderr)
        return 1
    finally:
        session.close()

    _print_stats(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
