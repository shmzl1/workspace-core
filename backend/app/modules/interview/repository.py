"""Interview repository for Sprint 1 outer workflow."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.interview.models import Interview, Interviewer, MeetingRoom
from app.modules.recruitment.models import CandidateApplication


class InterviewRepository:
    """Database reads for interview scheduling preview."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def application_exists(self, application_id: int) -> bool:
        return self.session.scalar(
            select(CandidateApplication.id).where(CandidateApplication.id == application_id)
        ) is not None

    def list_interviewers(self) -> list[Interviewer]:
        return list(
            self.session.scalars(
                select(Interviewer).where(Interviewer.is_active.is_(True)).order_by(Interviewer.id)
            ).all()
        )

    def list_meeting_rooms(self) -> list[MeetingRoom]:
        return list(
            self.session.scalars(
                select(MeetingRoom).where(MeetingRoom.is_active.is_(True)).order_by(MeetingRoom.id)
            ).all()
        )

    def list_interviews(self) -> list[Interview]:
        return list(self.session.scalars(select(Interview).order_by(Interview.start_at.desc()).limit(50)).all())
