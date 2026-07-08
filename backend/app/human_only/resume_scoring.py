from __future__ import annotations

from typing import Any


def score_resume(payload: dict[str, Any] | None) -> dict[str, Any]:
    data = payload or {}
    candidate = data.get("candidate") if isinstance(data.get("candidate"), dict) else {}
    job = data.get("job") if isinstance(data.get("job"), dict) else {}

    candidate_skills = get_list(candidate, "skills")
    job_skills = get_list(job, "required_skills") + get_list(job, "preferred_skills")
    candidate_projects = get_list(candidate, "projects") or get_list(candidate, "project_keywords")
    job_projects = get_list(job, "keywords") or job_skills

    skill_score, matched_skills, missing_skills = calc_skill_score(candidate_skills, job_skills)
    experience_score = calc_experience_score(candidate, job)
    project_score = calc_project_score(candidate_projects + candidate_skills, job_projects)
    risk_tags = find_risks(candidate, missing_skills, experience_score, project_score)
    risk_score = max(40, 100 - len(risk_tags) * 15)

    total = (
        skill_score * 0.40
        + experience_score * 0.25
        + project_score * 0.20
        + risk_score * 0.15
    )
    total = round(limit_score(total), 2)
    match_rate = round(limit_score(total * 0.7 + skill_score * 0.3), 2)
    action = make_action(total, risk_tags)

    skill_text = (
        f"已匹配技能：{'、'.join(matched_skills) or '暂无'}；"
        f"待补充技能：{'、'.join(missing_skills) or '无'}。"
    )
    experience_text = f"经验匹配得分 {experience_score}，候选人经验约 {round(get_years(candidate), 1)} 年。"
    education_text = make_education_text(candidate)
    risk_text = "；".join(risk_tags) if risk_tags else "未发现明显风险。"
    basis = [
        f"技能匹配得分 {skill_score}，核心技能覆盖情况已计入总分。",
        f"经验匹配得分 {experience_score}，与岗位最低经验要求进行比较。",
        f"项目匹配得分 {project_score}，根据项目关键词和岗位关键词重合度计算。",
        f"风险项：{risk_text}",
    ]

    return {
        "status": "success",
        "message": "智能评估结果已生成。",
        "score_total": total,
        "overall_score": total,
        "match_score": match_rate,
        "match_rate": match_rate,
        "skill_match": skill_text,
        "experience_match": experience_text,
        "education_match": education_text,
        "risk_tags": risk_tags,
        "risk_prompt": risk_text,
        "recommended_action": action,
        "recommendation": action,
        "scoring_basis": basis,
        "reasons": basis,
        "missing_skills": missing_skills,
        "experience_score": experience_score,
        "score_breakdown": {
            "skill": skill_score,
            "experience": experience_score,
            "project": project_score,
            "risk": risk_score,
        },
        "explanation": {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "score_rule": "技能40%，经验25%，项目20%，风险15%。学历作为补充说明和风险参考。",
        },
    }


def get_list(source: dict[str, Any], key: str) -> list[str]:
    value = source.get(key)
    if value is None and isinstance(source.get("profile_json"), dict):
        value = source["profile_json"].get(key)
    if value is None:
        return []
    if isinstance(value, str):
        parts = value.replace("；", ",").replace("、", ",").split(",")
        return [part.strip().lower() for part in parts if part.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    return [str(value).strip().lower()]


def get_number(source: dict[str, Any], *keys: str) -> float:
    for key in keys:
        value = source.get(key)
        if value is None and isinstance(source.get("profile_json"), dict):
            value = source["profile_json"].get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
    return 0.0


def get_years(candidate: dict[str, Any]) -> float:
    years = get_number(candidate, "years_of_experience", "experience_years")
    if years:
        return years
    return get_number(candidate, "experience_months") / 12


def calc_skill_score(candidate_skills: list[str], job_skills: list[str]) -> tuple[float, list[str], list[str]]:
    required = sorted(set(job_skills))
    current = set(candidate_skills)
    if not required:
        return (75.0 if current else 60.0), sorted(current), []
    matched = [skill for skill in required if skill in current]
    missing = [skill for skill in required if skill not in current]
    score = len(matched) / len(required) * 100
    return round(limit_score(score), 2), matched, missing


def calc_experience_score(candidate: dict[str, Any], job: dict[str, Any]) -> float:
    years = get_years(candidate)
    need_years = get_number(job, "min_years")
    if not need_years:
        need_years = get_number(job, "min_experience_months") / 12
    if need_years <= 0:
        return 80.0 if years > 0 else 65.0
    if years >= need_years:
        return round(limit_score(85 + min((years - need_years) * 4, 15)), 2)
    return round(limit_score(years / need_years * 80), 2)


def calc_project_score(candidate_items: list[str], job_items: list[str]) -> float:
    target = sorted(set(job_items))
    source = set(candidate_items)
    if not target:
        return 70.0 if source else 55.0
    matched = [item for item in target if item in source]
    return round(limit_score(len(matched) / len(target) * 100), 2)


def find_risks(candidate: dict[str, Any], missing_skills: list[str], experience_score: float, project_score: float) -> list[str]:
    risks: list[str] = []
    if missing_skills:
        risks.append("关键技能缺失")
    if experience_score < 70:
        risks.append("经验年限不足")
    if project_score < 60:
        risks.append("项目经历匹配度偏低")
    if get_number(candidate, "job_hopping_count") >= 3:
        risks.append("稳定性需复核")
    education = str(candidate.get("education") or candidate.get("profile_json", {}).get("education") or "")
    if education and any(word in education.lower() for word in ["college", "专科", "高中"]):
        risks.append("学历背景需结合项目经验复核")
    return risks


def make_action(score: float, risk_tags: list[str]) -> str:
    if score >= 85 and len(risk_tags) <= 1:
        return "建议优先面试"
    if score >= 70:
        return "建议进入初筛复核"
    if score >= 55:
        return "建议补充简历材料后再评估"
    return "建议暂缓推进"


def make_education_text(candidate: dict[str, Any]) -> str:
    value = candidate.get("education")
    if value is None and isinstance(candidate.get("profile_json"), dict):
        value = candidate["profile_json"].get("education")
    if value:
        return f"学历信息为 {value}，作为岗位适配的补充参考。"
    return "简历中未提供明确学历信息，建议在沟通中补充确认。"


def limit_score(value: float) -> float:
    return max(0.0, min(100.0, float(value)))
