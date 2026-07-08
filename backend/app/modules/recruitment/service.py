"""Recruitment service for Sprint 1 outer workflow."""

from decimal import Decimal
from importlib import import_module
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


class RecruitmentService:
    """Orchestrates recruitment reads and human-only scoring calls."""

    def __init__(self, repository: RecruitmentRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: Session) -> "RecruitmentService":
        return cls(RecruitmentRepository(session))

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
            ready_message="Sprint 1 外层已提供招聘评分入口；真实评分依赖黄钧人工禁飞区接入。",
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
            return ScoreApplicationResponse(
                application_id=application_id,
                status="HUMAN_ONLY_ALGORITHM_NOT_READY",
                message="招聘评分禁飞区尚未由黄钧人工接入。",
                requires_human_only=True,
                explanation={
                    "expected_entry": "backend/app/human_only/resume_scoring.py::score_resume(...)",
                    "service_entry": "RecruitmentService.score_application(...)",
                },
            )

        detail = self.repository.get_application_detail(application_id)
        if detail is None:
            raise TalentFlowError("APPLICATION_NOT_FOUND", "候选人申请不存在。")

        application, candidate, job = detail
        scoring_input = {
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
        candidate_result = score_resume(scoring_input)
        score_total = candidate_result.get("score_total")
        score_breakdown = candidate_result.get("score_breakdown", {})
        self.repository.save_application_score(
            application,
            score_total,
            self._json_ready(score_breakdown),
            self._json_ready(dict(payload.weights)),
        )
        return ScoreApplicationResponse(
            application_id=application_id,
            status="SCORED",
            message="评分结果已由禁飞区公开函数返回。",
            score_total=score_total,
            score_breakdown=score_breakdown,
            explanation=candidate_result.get("explanation", {}),
            requires_human_only=False,
        )

    @staticmethod
    def _load_score_resume() -> Any | None:
        try:
            module = import_module("app.human_only.resume_scoring")
        except ModuleNotFoundError:
            return None
        return getattr(module, "score_resume", None)

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
