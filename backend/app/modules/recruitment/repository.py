"""Recruitment repository database reads."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.recruitment.models import Candidate, CandidateApplication, Job


class RecruitmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_jobs(self) -> list[Job]:
        return list(self.session.scalars(select(Job).order_by(Job.id)))

    def list_candidates(self) -> list[Candidate]:
        return list(self.session.scalars(select(Candidate).order_by(Candidate.id)))

    def list_applications_for_job(self, job_id: int) -> list[tuple[CandidateApplication, Candidate]]:
        stmt = (
            select(CandidateApplication, Candidate)
            .join(Candidate, Candidate.id == CandidateApplication.candidate_id)
            .where(CandidateApplication.job_id == job_id)
            .order_by(CandidateApplication.score_total.desc().nullslast(), CandidateApplication.id)
        )
        return list(self.session.execute(stmt).all())
