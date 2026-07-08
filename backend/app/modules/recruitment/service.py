"""Recruitment service."""

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules._serialization import model_to_dict
from app.modules.recruitment.repository import RecruitmentRepository
from app.modules.recruitment.schemas import (
    CandidateApplicationRead,
    CandidateRead,
    JobRead,
    RecruitmentDashboardRead,
    ScoreApplicationRequest,
    ScoreApplicationResponse,
)
from app.shared.human_only_bridge import HumanOnlyContract, algorithm_not_ready, load_human_only_function


RESUME_SCORING_CONTRACT = HumanOnlyContract(
    module_name="app.human_only.resume_scoring",
    file_path="backend/app/human_only/resume_scoring.py",
    function_name="score_resume",
    not_ready_message="智能评估服务暂未完成配置",
)


class RecruitmentService:
    """Orchestrates recruitment reads and human-only scoring calls."""

    def __init__(self, session_or_repository: Session | RecruitmentRepository) -> None:
        if isinstance(session_or_repository, RecruitmentRepository):
            self.repository = session_or_repository
        else:
            self.repository = RecruitmentRepository(session_or_repository)

    @classmethod
    def from_session(cls, session: Session) -> "RecruitmentService":
        return cls(session)

    def get_dashboard(self) -> RecruitmentDashboardRead:
        jobs = self.repository.list_jobs()
        candidates = self.repository.list_candidates()
        applications = self.repository.list_applications()
        pending = [row for row in applications if row[0].score_total is None]
        return RecruitmentDashboardRead(
            jobs_count=len(jobs),
            candidates_count=len(candidates),
            applications_count=len(applications),
            pending_score_count=len(pending),
            ready_message="招聘评分外层入口已就绪，真实评分结果依赖人工维护的核心算法接入。",
        )

    def list_jobs(self) -> list[JobRead]:
        return [JobRead.model_validate(job) for job in self.repository.list_jobs()]

    def list_candidates(self) -> list[CandidateRead]:
        return [CandidateRead.model_validate(candidate) for candidate in self.repository.list_candidates()]

    def list_applications(self) -> list[CandidateApplicationRead]:
        return [
            CandidateApplicationRead(
                id=application.id,
                candidate_id=application.candidate_id,
                candidate_name=candidate.full_name if candidate else None,
                job_id=application.job_id,
                job_title=job.title if job else None,
                current_stage=application.current_stage,
                score_total=application.score_total,
                score_breakdown=application.score_breakdown or {},
                weights_snapshot=application.weights_snapshot or {},
                scored_at=application.scored_at,
            )
            for application, candidate, job in self.repository.list_applications()
        ]

    def list_applications_for_job(self, job_id: int) -> list[dict]:
        results = []
        for application, candidate in self.repository.list_applications_for_job(job_id):
            results.append(
                {
                    "application": model_to_dict(
                        application,
                        [
                            "id",
                            "candidate_id",
                            "job_id",
                            "current_stage",
                            "score_total",
                            "score_breakdown",
                            "weights_snapshot",
                            "scored_at",
                            "applied_at",
                        ],
                    ),
                    "candidate": model_to_dict(
                        candidate,
                        ["id", "candidate_no", "full_name", "skills", "experience_months", "available_from"],
                    ),
                }
            )
        return results

    def score_application(self, application_id: int, payload: ScoreApplicationRequest) -> ScoreApplicationResponse:
        score_resume = self._load_score_resume()
        if score_resume is None:
            not_ready = algorithm_not_ready(
                RESUME_SCORING_CONTRACT,
                {"application_id": application_id, "weights": self._json_ready(dict(payload.weights))},
            )
            return ScoreApplicationResponse(
                application_id=application_id,
                status=not_ready["status"],
                message=not_ready["message"],
                expected_module=not_ready["expected_module"],
                expected_function=not_ready["expected_function"],
                fallback_data=not_ready["fallback_data"],
                requires_human_only=True,
            )

        detail = self.repository.get_application_detail(application_id)
        if detail is None:
            raise TalentFlowError("APPLICATION_NOT_FOUND", "候选人申请不存在。")

        application, candidate, job = detail
        input_payload = {
            "job": {
                "id": job.id,
                "title": job.title,
                "required_skills": job.required_skills or [],
                "preferred_skills": job.preferred_skills or [],
                "min_experience_months": job.min_experience_months,
            },
            "candidate": {
                "id": candidate.id,
                "full_name": candidate.full_name,
                "skills": candidate.skills or [],
                "experience_months": candidate.experience_months,
                "available_from": candidate.available_from.isoformat() if candidate.available_from else None,
                "profile_json": candidate.profile_json or {},
            },
            "weights": self._json_ready(dict(payload.weights)),
        }
        try:
            result = score_resume(input_payload)
        except NotImplementedError:
            not_ready = algorithm_not_ready(RESUME_SCORING_CONTRACT, {"application_id": application_id})
            return ScoreApplicationResponse(
                application_id=application_id,
                status=not_ready["status"],
                message=not_ready["message"],
                expected_module=not_ready["expected_module"],
                expected_function=not_ready["expected_function"],
                fallback_data=not_ready["fallback_data"],
                requires_human_only=True,
            )

        score_total = result.get("score_total", result.get("total_score"))
        match_score = result.get("match_score", result.get("job_match_score"))
        score_breakdown = result.get("score_breakdown", {})
        self.repository.save_application_score(
            application,
            score_total,
            self._json_ready(score_breakdown),
            self._json_ready(dict(payload.weights)),
        )
        return ScoreApplicationResponse(
            application_id=application_id,
            status=result.get("status", "scored"),
            message=result.get("message", "智能评估结果已生成。"),
            score_total=score_total,
            match_score=match_score,
            skill_match=result.get("skill_match"),
            experience_match=result.get("experience_match"),
            education_match=result.get("education_match"),
            risk_tags=result.get("risk_tags", []),
            risk_prompt=result.get("risk_prompt"),
            recommended_action=result.get("recommended_action"),
            scoring_basis=result.get("scoring_basis", []),
            score_breakdown=score_breakdown,
            explanation=result.get("explanation", {}),
            requires_human_only=False,
        )

    @staticmethod
    def _load_score_resume() -> Any | None:
        return load_human_only_function(RESUME_SCORING_CONTRACT)

    @classmethod
    def _json_ready(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: cls._json_ready(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._json_ready(item) for item in value]
        if isinstance(value, Decimal):
            return float(value)
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return value
