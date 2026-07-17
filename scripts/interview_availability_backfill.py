"""Idempotent planning and persistence for demo candidate availability."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.interview.models import Interview, Interviewer, InterviewSlot, MeetingRoom
from app.modules.recruitment.models import CandidateApplication


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
) -> CandidateAvailabilityBackfillStats:
    """Add demo availability only for applicants without a valid future slot.

    The caller owns the transaction. Existing slots are never updated or deleted.
    """

    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if slots_per_candidate < 1:
        raise ValueError("slots_per_candidate must be positive")

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
    )
    if not shared_windows:
        raise RuntimeError("面试官和会议室没有至少 60 分钟且未被占用的未来交集，候选人可用时间补全已停止。")

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
