from app.human_only.resume_scoring import score_resume


def test_high_match_candidate_gets_high_score() -> None:
    result = score_resume(
        {
            "candidate": {
                "skills": ["Python", "SQL", "Machine Learning", "RAG"],
                "years_of_experience": 8,
                "education": "master",
                "projects": ["RAG", "data governance"],
            },
            "job": {
                "required_skills": ["Python", "SQL", "Machine Learning"],
                "preferred_skills": ["RAG"],
                "min_years": 5,
                "required_education": "bachelor",
                "keywords": ["RAG", "data governance"],
            },
        }
    )

    assert result["status"] == "success"
    assert result["overall_score"] >= 85
    assert result["recommendation"] == "建议优先面试"


def test_missing_required_skill_produces_risk_tag() -> None:
    result = score_resume(
        {
            "candidate": {"skills": ["Python"], "years_of_experience": 5, "education": "bachelor"},
            "job": {"required_skills": ["Python", "SQL"], "min_years": 3, "required_education": "bachelor"},
        }
    )

    assert "SQL".lower() in result["missing_skills"]
    assert "关键技能缺失" in result["risk_tags"]


def test_insufficient_experience_reduces_score() -> None:
    result = score_resume(
        {
            "candidate": {"skills": ["Python", "SQL"], "years_of_experience": 1, "education": "bachelor"},
            "job": {"required_skills": ["Python", "SQL"], "min_years": 5, "required_education": "bachelor"},
        }
    )

    assert result["experience_score"] < 70
    assert "经验年限不足" in result["risk_tags"]


def test_missing_fields_do_not_crash() -> None:
    result = score_resume({})

    assert result["status"] == "success"
    assert 0 <= result["overall_score"] <= 100
    assert isinstance(result["reasons"], list)
