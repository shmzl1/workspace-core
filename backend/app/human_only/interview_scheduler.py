from __future__ import annotations
from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import Any
def schedule_interview(payload: dict[str, Any] | None) -> dict[str, Any]:
    data = payload or {}
    duration = int(data.get("duration_minutes") or 60)
    candidate = data.get("candidate") if isinstance(data.get("candidate"), dict) else {}
    candidate_name = data.get("candidate_name") or candidate.get("name") or "候选人"
    candidate_slots = read_slots(data.get("candidate_available_slots") or candidate.get("available_slots"))
    interviewers = data.get("interviewers") if isinstance(data.get("interviewers"), list) else []
    rooms = data.get("meeting_rooms") or data.get("rooms") or []
    conflicts = data.get("existing_interviews") if isinstance(data.get("existing_interviews"), list) else []
    if not candidate_slots or not interviewers:
        return {
            "status": "invalid_input",
            "message": "排期数据不足，无法生成建议。",
            "recommended_slots": [],
            "best_slot": None,
            "reasons": ["缺少候选人或面试官可用时间。"],
            "conflicts": [],
            "conflict_explanation": {"reason": "缺少候选人或面试官可用时间。"},
        }
    room_list = rooms if isinstance(rooms, list) and rooms else [{"room_name": "线上会议", "available_slots": []}]
    options: list[dict[str, Any]] = []
    conflict_notes: list[dict[str, str]] = []
    for candidate_slot in candidate_slots:
        for interviewer in interviewers:
            interviewer_slots = read_slots(interviewer.get("available_slots") if isinstance(interviewer, dict) else [])
            for interviewer_slot in interviewer_slots:
                common_slot = overlap(candidate_slot, interviewer_slot)
                if not common_slot or not enough_time(common_slot, duration):
                    continue
                room_options, room_conflicts = _find_room_options_for_slot(
                    common_slot, duration, candidate, interviewer, room_list, conflicts,
                )
                options.extend(room_options)
                conflict_notes.extend(room_conflicts)
    if not options:
        return {
            "status": "no_available_slot",
            "message": "暂无合适面试时间。",
            "recommended_slots": [],
            "best_slot": None,
            "reasons": ["候选人、面试官和会议室暂无满足时长要求的交集。"],
            "conflicts": conflict_notes,
            "conflict_detection": "存在时间冲突或资源不可用。",
            "conflict_explanation": {"conflicts": conflict_notes},
        }
    options.sort(key=lambda item: (-item["score"], item["start"]))
    best = options[0]
    slots = [serialize_slot(item) for item in options[:5]]
    best_slot = slots[0]
    reason = "；".join(best["reasons"])
    return {
        "status": "success",
        "message": "已生成智能排期建议。",
        "recommended_time": {"start": best_slot["start"], "end": best_slot["end"]},
        "recommended_interviewer_id": best_slot["interviewer_id"],
        "recommended_interviewer": best_slot["interviewer"],
        "recommended_room_id": best_slot["room_id"],
        "recommended_room": best_slot["room"],
        "interviewer_availability": f"{best_slot['interviewer']} 在该时间段可用。",
        "candidate_availability": f"{candidate_name} 在该时间段可用。",
        "conflict_detection": "未发现冲突。",
        "recommendation_reason": f"{reason}；推荐评分 {best_slot['score']}。",
        "conflict_explanation": {"conflicts": conflict_notes, "priority_score": best_slot["score"]},
        "recommended_slots": slots,
        "best_slot": best_slot,
        "reasons": best["reasons"],
        "conflicts": conflict_notes,
    }
def parse_time(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not value:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None
def read_slots(value: Any) -> list[dict[str, datetime]]:
    if not isinstance(value, list):
        return []
    slots: list[dict[str, datetime]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        start = parse_time(item.get("start") or item.get("start_time"))
        end = parse_time(item.get("end") or item.get("end_time"))
        if start and end and end > start:
            slots.append({"start": start, "end": end})
    return slots
def overlap(first: dict[str, datetime], second: dict[str, datetime]) -> dict[str, datetime] | None:
    start = max(first["start"], second["start"])
    end = min(first["end"], second["end"])
    if end <= start:
        return None
    return {"start": start, "end": end}
def enough_time(slot: dict[str, datetime], duration_minutes: int) -> bool:
    return slot["end"] - slot["start"] >= timedelta(minutes=duration_minutes)


def generate_fixed_slots(
    slot: dict[str, datetime],
    duration_minutes: int,
    step_minutes: int = 15,
) -> Iterator[dict[str, datetime]]:
    """Yield fixed-duration candidates across the whole availability window."""
    if duration_minutes <= 0 or step_minutes <= 0:
        return
    duration = timedelta(minutes=duration_minutes)
    step = timedelta(minutes=step_minutes)
    current = slot["start"]
    while current + duration <= slot["end"]:
        yield {"start": current, "end": current + duration}
        current += step


def has_conflict(
    slot: dict[str, datetime],
    conflicts: list[dict[str, Any]],
    candidate_id: Any,
    interviewer_id: Any,
    room_id: Any,
) -> bool:
    for event in conflicts:
        if not isinstance(event, dict):
            continue
        event_slot = {
            "start": parse_time(event.get("start")),
            "end": parse_time(event.get("end")),
        }
        if not event_slot["start"] or not event_slot["end"] or not overlap(slot, event_slot):
            continue
        if (
            event.get("candidate_id") == candidate_id
            or event.get("interviewer_id") == interviewer_id
            or event.get("meeting_room_id") == room_id
        ):
            return True
    return False
def score_slot(start: datetime, end: datetime, interviewer_load: int) -> tuple[int, list[str]]:
    score = 40
    reasons = ["候选人、面试官和会议资源时间重合"]
    if 9 <= start.hour and end.hour <= 18:
        score += 25
        reasons.append("位于标准工作时间")
    if start.hour < 12:
        score += 15
        reasons.append("上午时段便于后续复盘")
    elif start.hour < 16:
        score += 10
        reasons.append("下午核心面试时段")
    load_bonus = max(0, 10 - min(interviewer_load * 2, 10))
    if load_bonus:
        score += load_bonus
        reasons.append("面试官当日负载较低")
    return min(score, 100), reasons
def make_option(
    slot: dict[str, datetime],
    duration: int,
    candidate_id: Any,
    interviewer: dict[str, Any],
    room: dict[str, Any],
    conflicts: list[dict[str, Any]],
) -> dict[str, Any]:
    start = slot["start"]
    end = start + timedelta(minutes=duration)
    fixed_slot = {"start": start, "end": end}
    load = int(interviewer.get("load") or interviewer.get("scheduled_count") or 0)
    score, reasons = score_slot(start, end, load)
    return {
        "start": start,
        "end": end,
        "interviewer_id": interviewer.get("interviewer_id") or interviewer.get("id"),
        "interviewer": interviewer.get("employee_name") or interviewer.get("name") or "面试官",
        "room_id": room.get("meeting_room_id") or room.get("id"),
        "room": room.get("room_name") or room.get("name") or "线上会议",
        "has_conflict": has_conflict(
            fixed_slot,
            conflicts,
            candidate_id,
            interviewer.get("interviewer_id") or interviewer.get("id"),
            room.get("meeting_room_id") or room.get("id"),
        ),
        "score": score,
        "reasons": reasons,
    }
def serialize_slot(slot: dict[str, Any]) -> dict[str, Any]:
    return {
        "start": format_time(slot["start"]),
        "end": format_time(slot["end"]),
        "score": slot["score"],
        "interviewer_id": slot["interviewer_id"],
        "interviewer": slot["interviewer"],
        "room_id": slot["room_id"],
        "room": slot["room"],
        "conflict": slot["has_conflict"],
        "reasons": slot["reasons"],
    }
def format_time(value: datetime) -> str:
    return value.isoformat(timespec="minutes")


def _find_room_options_for_slot(
    common_slot: dict[str, datetime],
    duration: int,
    candidate: dict[str, Any],
    interviewer: dict[str, Any],
    room_list: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Evaluate room availability for a shared candidate-interviewer time slot."""
    options: list[dict[str, Any]] = []
    conflict_notes: list[dict[str, str]] = []
    for room in room_list:
        room_slots = read_slots(room.get("available_slots") if isinstance(room, dict) else [])
        usable_slots = [common_slot]
        if room_slots:
            matches = [overlap(common_slot, room_slot) for room_slot in room_slots]
            matches = [item for item in matches if item and enough_time(item, duration)]
            if not matches:
                continue
            usable_slots = matches
        for usable_slot in usable_slots:
            for fixed_slot in generate_fixed_slots(usable_slot, duration):
                option = make_option(
                    fixed_slot,
                    duration,
                    candidate.get("candidate_id"),
                    interviewer,
                    room,
                    conflicts,
                )
                if option["has_conflict"]:
                    conflict_notes.append(
                        {
                            "type": "event_conflict",
                            "message": f"{format_time(option['start'])} 存在已占用日程。",
                        }
                    )
                    continue
                options.append(option)
    return options, conflict_notes
