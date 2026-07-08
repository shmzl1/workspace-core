"""Deterministic interview scheduling algorithm."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


def schedule_interview(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Generate interview time recommendations from availability and conflicts."""

    normalized = normalize_schedule_request(payload or {})
    if normalized.get("error"):
        return {
            "status": "invalid_input",
            "message": normalized["error"],
            "recommended_slots": [],
            "conflicts": normalized.get("conflicts", []),
            "reasons": [],
        }

    recommendations = build_recommendation(normalized)
    if not recommendations:
        return {
            "status": "no_available_slot",
            "message": "暂无合适面试时间",
            "best_slot": None,
            "recommended_slots": [],
            "conflicts": normalized["conflicts"],
            "reasons": ["候选人、面试官和会议室时间暂无满足时长要求的交集。"],
            "conflict_explanation": {"conflicts": normalized["conflicts"]},
        }

    sorted_slots = sort_recommendations(recommendations)
    best = sorted_slots[0]
    interviewer_name = best.get("interviewer") or "面试官"
    reason_text = "；".join(best["reasons"])

    return {
        "status": "success",
        "message": "已生成智能排期建议",
        "best_slot": best,
        "recommended_slots": sorted_slots,
        "conflicts": normalized["conflicts"],
        "reasons": best["reasons"],
        "recommended_time": {"start": best["start"], "end": best["end"]},
        "recommended_interviewer_id": best.get("interviewer_id"),
        "recommended_room_id": best.get("room_id"),
        "interviewer_availability": f"{interviewer_name} 在该时间段可用。",
        "candidate_availability": f"{normalized['candidate_name']} 在该时间段可用。",
        "conflict_detection": "未发现冲突。" if not best["conflict"] else "存在冲突，建议人工复核。",
        "recommendation_reason": f"{reason_text}；推荐评分 {best['score']}。",
        "conflict_explanation": {
            "conflicts": normalized["conflicts"],
            "priority_score": best["score"],
            "position": normalized["position"],
        },
    }


def normalize_schedule_request(raw: dict[str, Any]) -> dict[str, Any]:
    candidate = raw.get("candidate") if isinstance(raw.get("candidate"), dict) else {}
    candidate_slots = raw.get("candidate_available_slots") or candidate.get("available_slots") or []
    interviewers = normalize_interviewers(raw)
    rooms = normalize_rooms(raw)
    duration = safe_int(raw.get("duration_minutes"), 60)
    existing_events = [slot for slot in normalize_slots(raw.get("existing_events") or raw.get("conflicts") or [])]

    parsed_candidate_slots = normalize_slots(candidate_slots)
    conflicts: list[dict[str, str]] = []
    if candidate_slots and not parsed_candidate_slots:
        conflicts.append({"type": "invalid_time", "message": "候选人可用时间格式无法识别。"})

    if not parsed_candidate_slots:
        return {"error": "排期数据不足，无法生成建议", "conflicts": conflicts}
    if not interviewers:
        return {"error": "排期数据不足，无法生成建议", "conflicts": conflicts}
    if duration <= 0:
        return {"error": "面试时长无效，无法生成建议", "conflicts": conflicts}

    return {
        "candidate_name": raw.get("candidate_name") or candidate.get("name") or "候选人",
        "position": raw.get("position") or raw.get("job_title") or "",
        "candidate_slots": parsed_candidate_slots,
        "interviewers": interviewers,
        "rooms": rooms,
        "existing_events": existing_events,
        "duration_minutes": duration,
        "conflicts": conflicts,
    }


def normalize_interviewers(raw: dict[str, Any]) -> list[dict[str, Any]]:
    source = raw.get("interviewers") or []
    if not source and raw.get("interviewer_available_slots"):
        source = [{"interviewer_id": None, "employee_name": "面试官", "available_slots": raw["interviewer_available_slots"]}]

    interviewers = []
    for item in source:
        if not isinstance(item, dict):
            continue
        slots = normalize_slots(item.get("available_slots") or item.get("slots") or [])
        if not slots:
            continue
        interviewers.append(
            {
                "id": item.get("interviewer_id") or item.get("id"),
                "name": item.get("employee_name") or item.get("name") or "面试官",
                "available_slots": slots,
                "load": safe_int(item.get("load") or item.get("scheduled_count"), 0),
            }
        )
    return interviewers


def normalize_rooms(raw: dict[str, Any]) -> list[dict[str, Any]]:
    source = raw.get("meeting_rooms") or raw.get("rooms") or []
    rooms = []
    for item in source:
        if not isinstance(item, dict):
            continue
        slots = normalize_slots(item.get("available_slots") or item.get("slots") or [])
        if not slots:
            continue
        rooms.append(
            {
                "id": item.get("meeting_room_id") or item.get("id"),
                "name": item.get("room_name") or item.get("name") or "会议室",
                "available_slots": slots,
            }
        )
    if not rooms:
        rooms.append({"id": None, "name": "线上会议", "available_slots": []})
    return rooms


def normalize_slots(values: Any) -> list[dict[str, datetime]]:
    slots = []
    if not isinstance(values, list):
        return slots
    for item in values:
        if not isinstance(item, dict):
            continue
        start = parse_time(item.get("start") or item.get("start_time"))
        end = parse_time(item.get("end") or item.get("end_time"))
        if start and end and end > start:
            slots.append({"start": start, "end": end})
    return slots


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


def build_recommendation(request: dict[str, Any]) -> list[dict[str, Any]]:
    recommendations = []
    duration = timedelta(minutes=request["duration_minutes"])
    for candidate_slot in request["candidate_slots"]:
        for interviewer in request["interviewers"]:
            for interviewer_slot in interviewer["available_slots"]:
                overlap = get_overlap(candidate_slot, interviewer_slot)
                if not overlap or not enough_duration(overlap, duration):
                    continue
                for room in request["rooms"]:
                    room_overlap = overlap
                    if room["available_slots"]:
                        room_overlaps = [get_overlap(overlap, room_slot) for room_slot in room["available_slots"]]
                        valid_room_overlaps = [
                            item for item in room_overlaps if item and enough_duration(item, duration)
                        ]
                        if not valid_room_overlaps:
                            continue
                        room_overlap = valid_room_overlaps[0]
                    conflict = has_conflict(room_overlap, request["existing_events"])
                    if conflict:
                        request["conflicts"].append(
                            {
                                "type": "event_conflict",
                                "message": f"{format_dt(room_overlap['start'])} 存在已占用日程。",
                            }
                        )
                        continue
                    slot_end = room_overlap["start"] + duration
                    slot = {
                        "start": room_overlap["start"],
                        "end": slot_end,
                        "interviewer": interviewer,
                        "room": room,
                        "conflict": False,
                    }
                    slot["score"], slot["reasons"] = calculate_slot_score(slot, interviewer)
                    recommendations.append(serialize_slot(slot))
    return recommendations


def get_overlap(first: dict[str, datetime], second: dict[str, datetime]) -> dict[str, datetime] | None:
    start = max(first["start"], second["start"])
    end = min(first["end"], second["end"])
    if end <= start:
        return None
    return {"start": start, "end": end}


def enough_duration(slot: dict[str, datetime], duration: timedelta) -> bool:
    return slot["end"] - slot["start"] >= duration


def has_conflict(slot: dict[str, datetime], existing_events: list[dict[str, datetime]]) -> bool:
    return any(get_overlap(slot, event) for event in existing_events)


def calculate_slot_score(slot: dict[str, Any], interviewer: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    if not slot["conflict"]:
        score += 40
        reasons.append("该时间段无冲突")
    score += 25
    reasons.append("候选人与面试官时间重合")
    if is_working_hour(slot["start"], slot["end"]):
        score += 20
        reasons.append("处于工作时间")
    if slot["start"].hour < 12:
        score += 10
        reasons.append("时间较早，便于后续调整")
    elif slot["start"].hour < 16:
        score += 7
        reasons.append("位于下午核心面试时间")
    load_bonus = max(0, 5 - min(interviewer.get("load", 0), 5))
    score += load_bonus
    if load_bonus:
        reasons.append("面试官负载较低")
    return min(score, 100), reasons


def is_working_hour(start: datetime, end: datetime) -> bool:
    return 9 <= start.hour and end.hour <= 18


def serialize_slot(slot: dict[str, Any]) -> dict[str, Any]:
    return {
        "start": format_dt(slot["start"]),
        "end": format_dt(slot["end"]),
        "score": slot["score"],
        "conflict": slot["conflict"],
        "interviewer": slot["interviewer"].get("name", "面试官"),
        "interviewer_id": slot["interviewer"].get("id"),
        "room": slot["room"].get("name", "会议室"),
        "room_id": slot["room"].get("id"),
        "reasons": slot["reasons"],
    }


def sort_recommendations(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(slots, key=lambda item: (-item["score"], item["start"]))


def format_dt(value: datetime) -> str:
    return value.isoformat(timespec="minutes")


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
