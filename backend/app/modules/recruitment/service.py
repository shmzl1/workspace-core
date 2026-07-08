"""Recruitment service read models for Sprint 1 API wiring."""

from app.modules._serialization import model_to_dict
from app.modules.recruitment.repository import RecruitmentRepository
from sqlalchemy.orm import Session


class RecruitmentService:
    def __init__(self, repository: RecruitmentRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: Session) -> "RecruitmentService":
        return cls(RecruitmentRepository(session))

    def list_jobs(self) -> list[dict]:
        fields = [
            "id",
            "job_code",
            "title",
            "department",
            "description",
            "required_skills",
            "preferred_skills",
            "min_experience_months",
            "location",
            "employment_type",
            "status",
        ]
        return [model_to_dict(job, fields) for job in self.repository.list_jobs()]

    def list_candidates(self) -> list[dict]:
        fields = [
            "id",
            "candidate_no",
            "full_name",
            "email",
            "phone",
            "skills",
            "experience_months",
            "available_from",
            "source",
            "profile_json",
        ]
        return [model_to_dict(candidate, fields) for candidate in self.repository.list_candidates()]

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
