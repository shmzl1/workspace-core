"""Deterministic resume scoring algorithm."""

from __future__ import annotations

from typing import Any


EDUCATION_RANK = {
    "": 0,
    "none": 0,
    "high_school": 1,
    "associate": 2,
    "college": 3,
    "bachelor": 4,
    "本科": 4,
    "master": 5,
    "硕士": 5,
    "phd": 6,
    "doctor": 6,
    "博士": 6,
}


def score_resume(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Score a candidate against a job profile with explainable deterministic rules."""

    candidate = normalize_candidate((payload or {}).get("candidate", {}))
    job = normalize_job((payload or {}).get("job", {}))
    weights = normalize_weights((payload or {}).get("weights", {}))

    skill_result = calculate_skill_score(candidate, job)
    experience_score = calculate_experience_score(candidate, job)
    education_score = calculate_education_score(candidate, job)
    project_score = calculate_project_score(candidate, job)
    risks = detect_risks(candidate, job, skill_result, experience_score, education_score, project_score)

    weighted_score = (
        skill_result["score"] * weights["skill"]
        + experience_score * weights["experience"]
        + education_score * weights["education"]
        + project_score * weights["project"]
        + (100 - risks["risk_penalty"]) * weights["risk"]
    )
    overall_score = round(clamp_score(weighted_score), 2)
    match_rate = round(clamp_score((overall_score * 0.7) + (skill_result["score"] * 0.3)), 2)
    recommendation = make_recommendation(overall_score, risks["risk_tags"])
    reasons = build_reasons(skill_result, experience_score, education_score, project_score, risks["risk_tags"])

    return {
        "status": "success",
        "message": "智能评估结果已生成。",
        "overall_score": overall_score,
        "score_total": overall_score,
        "match_rate": match_rate,
        "match_score": match_rate,
        "skill_score": skill_result["score"],
        "experience_score": experience_score,
        "education_score": education_score,
        "project_score": project_score,
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "risk_tags": risks["risk_tags"],
        "recommendation": recommendation,
        "recommended_action": recommendation,
        "next_action": recommendation,
        "reasons": reasons,
        "scoring_basis": reasons,
        "skill_match": build_skill_match(skill_result),
        "experience_match": f"经验匹配得分 {experience_score}，候选人约 {candidate['years_of_experience']} 年经验。",
        "education_match": f"学历匹配得分 {education_score}。",
        "risk_prompt": "；".join(risks["risk_tags"]) if risks["risk_tags"] else "未发现明显风险。",
        "score_breakdown": {
            "skill": skill_result["score"],
            "experience": experience_score,
            "education": education_score,
            "project": project_score,
            "risk": 100 - risks["risk_penalty"],
        },
        "explanation": {
            "weights": weights,
            "risk_penalty": risks["risk_penalty"],
        },
    }


def normalize_candidate(raw: Any) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    profile = data.get("profile_json") if isinstance(data.get("profile_json"), dict) else {}
    skills = to_list(data.get("skills") or profile.get("skills"))
    projects = to_list(data.get("projects") or profile.get("projects") or profile.get("project_keywords"))
    years = data.get("years_of_experience", data.get("experience_years"))
    if years is None:
        months = data.get("experience_months", 0) or 0
        years = float(months) / 12

    return {
        "name": data.get("name") or data.get("full_name") or "",
        "skills": normalize_terms(skills),
        "years_of_experience": safe_float(years),
        "education": normalize_education(data.get("education") or profile.get("education")),
        "projects": normalize_terms(projects),
        "job_hopping_count": safe_int(data.get("job_hopping_count") or profile.get("job_hopping_count")),
        "expected_salary": parse_salary(data.get("expected_salary") or profile.get("expected_salary")),
        "current_status": str(data.get("current_status") or profile.get("current_status") or ""),
    }


def normalize_job(raw: Any) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    min_years = data.get("min_years")
    if min_years is None:
        min_years = safe_float(data.get("min_experience_months", 0)) / 12

    return {
        "title": str(data.get("title") or ""),
        "required_skills": normalize_terms(to_list(data.get("required_skills"))),
        "preferred_skills": normalize_terms(to_list(data.get("preferred_skills"))),
        "min_years": safe_float(min_years),
        "required_education": normalize_education(data.get("required_education") or data.get("education")),
        "keywords": normalize_terms(to_list(data.get("keywords"))),
        "salary_range": parse_salary_range(data.get("salary_range")),
    }


def normalize_weights(raw: Any) -> dict[str, float]:
    data = raw if isinstance(raw, dict) else {}
    weights = {
        "skill": safe_float(data.get("skill", 0.4)),
        "experience": safe_float(data.get("experience", data.get("work_experience", 0.2))),
        "education": safe_float(data.get("education", 0.15)),
        "project": safe_float(data.get("project", data.get("projects", 0.15))),
        "risk": safe_float(data.get("risk", 0.1)),
    }
    total = sum(weights.values()) or 1
    return {key: value / total for key, value in weights.items()}


def calculate_skill_score(candidate: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    required = set(job["required_skills"])
    preferred = set(job["preferred_skills"])
    skills = set(candidate["skills"])
    matched_required = sorted(required & skills)
    matched_preferred = sorted(preferred & skills)
    missing = sorted(required - skills)

    if not required and not preferred:
        score = 70
    else:
        required_score = (len(matched_required) / len(required) * 80) if required else 50
        preferred_score = (len(matched_preferred) / len(preferred) * 20) if preferred else 10
        score = required_score + preferred_score

    return {
        "score": round(clamp_score(score), 2),
        "matched_skills": sorted(set(matched_required + matched_preferred)),
        "missing_skills": missing,
    }


def calculate_experience_score(candidate: dict[str, Any], job: dict[str, Any]) -> float:
    required_years = job["min_years"]
    years = candidate["years_of_experience"]
    if required_years <= 0:
        return 80 if years > 0 else 60
    if years >= required_years:
        extra = min((years - required_years) * 4, 15)
        return round(clamp_score(85 + extra), 2)
    return round(clamp_score((years / required_years) * 80), 2)


def calculate_education_score(candidate: dict[str, Any], job: dict[str, Any]) -> float:
    required = EDUCATION_RANK.get(job["required_education"], 0)
    actual = EDUCATION_RANK.get(candidate["education"], 0)
    if required <= 0:
        return 80 if actual > 0 else 65
    if actual >= required:
        return 100
    gap = required - actual
    return round(clamp_score(100 - gap * 25), 2)


def calculate_project_score(candidate: dict[str, Any], job: dict[str, Any]) -> float:
    keywords = set(job["keywords"] or job["required_skills"] + job["preferred_skills"])
    projects = set(candidate["projects"] + candidate["skills"])
    if not keywords:
        return 70 if projects else 55
    matched = keywords & projects
    return round(clamp_score((len(matched) / len(keywords)) * 100), 2)


def detect_risks(
    candidate: dict[str, Any],
    job: dict[str, Any],
    skill_result: dict[str, Any],
    experience_score: float,
    education_score: float,
    project_score: float,
) -> dict[str, Any]:
    risk_tags: list[str] = []
    penalty = 0

    if skill_result["missing_skills"]:
        risk_tags.append("关键技能缺失")
        penalty += min(25, 8 * len(skill_result["missing_skills"]))
    if experience_score < 70:
        risk_tags.append("经验年限不足")
        penalty += 15
    if education_score < 80:
        risk_tags.append("学历不完全匹配")
        penalty += 8
    if project_score < 55:
        risk_tags.append("项目经历不足")
        penalty += 10
    if candidate["job_hopping_count"] >= 3:
        risk_tags.append("稳定性风险")
        penalty += 10
    if salary_out_of_range(candidate["expected_salary"], job["salary_range"]):
        risk_tags.append("期望薪资偏离岗位范围")
        penalty += 8

    return {"risk_tags": risk_tags, "risk_penalty": min(penalty, 60)}


def make_recommendation(score: float, risk_tags: list[str]) -> str:
    high_risk = {"关键技能缺失", "经验年限不足"}
    has_high_risk = any(tag in high_risk for tag in risk_tags)
    if score >= 85 and not has_high_risk:
        return "建议优先面试"
    if score >= 70:
        return "建议进入初筛复核"
    if score >= 55:
        return "建议补充材料后再评估"
    return "建议暂缓推进"


def build_reasons(
    skill_result: dict[str, Any],
    experience_score: float,
    education_score: float,
    project_score: float,
    risk_tags: list[str],
) -> list[str]:
    reasons = [
        f"技能匹配得分 {skill_result['score']}，匹配技能：{', '.join(skill_result['matched_skills']) or '暂无'}。",
        f"经验匹配得分 {experience_score}。",
        f"学历匹配得分 {education_score}。",
        f"项目关键词匹配得分 {project_score}。",
    ]
    if risk_tags:
        reasons.append(f"需关注风险：{'、'.join(risk_tags)}。")
    else:
        reasons.append("未发现明显风险项。")
    return reasons


def build_skill_match(skill_result: dict[str, Any]) -> str:
    matched = "、".join(skill_result["matched_skills"]) or "暂无"
    missing = "、".join(skill_result["missing_skills"]) or "无"
    return f"已匹配技能：{matched}；缺失技能：{missing}。"


def normalize_terms(values: list[Any]) -> list[str]:
    terms = []
    for item in values:
        text = str(item).strip().lower()
        if text:
            terms.append(text)
    return sorted(set(terms))


def normalize_education(value: Any) -> str:
    text = str(value or "").strip().lower()
    aliases = {
        "本科": "bachelor",
        "学士": "bachelor",
        "硕士": "master",
        "研究生": "master",
        "博士": "phd",
    }
    return aliases.get(text, text)


def to_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple | set):
        return list(value)
    if isinstance(value, str):
        return [part.strip() for part in value.replace("，", ",").split(",") if part.strip()]
    return [value]


def safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def parse_salary(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, int | float):
        return float(value)
    text = str(value).replace(",", "").replace("k", "000").replace("K", "000")
    digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")
    return safe_float(digits) if digits else None


def parse_salary_range(value: Any) -> tuple[float, float] | None:
    if isinstance(value, list | tuple) and len(value) >= 2:
        return safe_float(value[0]), safe_float(value[1])
    if isinstance(value, dict):
        low = value.get("min") or value.get("low")
        high = value.get("max") or value.get("high")
        if low is not None and high is not None:
            return safe_float(low), safe_float(high)
    return None


def salary_out_of_range(expected: float | None, salary_range: tuple[float, float] | None) -> bool:
    if expected is None or salary_range is None:
        return False
    low, high = salary_range
    if high <= 0:
        return False
    return expected > high * 1.15 or expected < low * 0.75


def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, float(value)))
