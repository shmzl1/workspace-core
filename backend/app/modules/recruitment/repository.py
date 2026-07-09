"""Recruitment repository."""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.recruitment.models import Candidate, CandidateApplication, Job


class RecruitmentRepository:
    """Database reads and writes for recruitment data."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_jobs(self) -> list[Job]:
        return list(self.session.scalars(select(Job).order_by(Job.id)).all())

    def list_candidates(self) -> list[Candidate]:
        return list(self.session.scalars(select(Candidate).order_by(Candidate.id)).all())

    def list_applications(self) -> list[tuple[CandidateApplication, Candidate | None, Job | None]]:
        rows = self.session.execute(
            select(CandidateApplication, Candidate, Job)
            .join(Candidate, Candidate.id == CandidateApplication.candidate_id, isouter=True)
            .join(Job, Job.id == CandidateApplication.job_id, isouter=True)
            .order_by(CandidateApplication.id)
        )
        return [(application, candidate, job) for application, candidate, job in rows.all()]

    def list_applications_for_job(self, job_id: int) -> list[tuple[CandidateApplication, Candidate]]:
        rows = self.session.execute(
            select(CandidateApplication, Candidate)
            .join(Candidate, Candidate.id == CandidateApplication.candidate_id)
            .where(CandidateApplication.job_id == job_id)
            .order_by(CandidateApplication.score_total.desc().nullslast(), CandidateApplication.id)
        )
        return [(application, candidate) for application, candidate in rows.all()]

    def get_application_detail(
        self,
        application_id: int,
    ) -> tuple[CandidateApplication, Candidate, Job] | None:
        row = self.session.execute(
            select(CandidateApplication, Candidate, Job)
            .join(Candidate, Candidate.id == CandidateApplication.candidate_id)
            .join(Job, Job.id == CandidateApplication.job_id)
            .where(CandidateApplication.id == application_id)
        ).one_or_none()
        if row is None:
            return None
        application, candidate, job = row
        return application, candidate, job

    def save_application_score(
        self,
        application: CandidateApplication,
        score_total: object,
        score_breakdown: dict[str, object],
        weights_snapshot: dict[str, object],
    ) -> CandidateApplication:
        application.score_total = score_total
        application.score_breakdown = score_breakdown
        application.weights_snapshot = weights_snapshot
        application.scored_at = datetime.now(timezone.utc)
        self.session.add(application)
        self.session.commit()
        self.session.refresh(application)
        return application
