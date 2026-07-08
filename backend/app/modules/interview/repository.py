"""Interview repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.interview.models import Interviewer, MeetingRoom
from app.modules.recruitment.models import CandidateApplication


class InterviewRepository:
    """Database reads for interview scheduling preview."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def application_exists(self, application_id: int) -> bool:
        return self.session.scalar(
            select(CandidateApplication.id).where(CandidateApplication.id == application_id)
        ) is not None

    def list_active_interviewers(self) -> list[Interviewer]:
        return list(self.session.scalars(select(Interviewer).where(Interviewer.is_active.is_(True))).all())

    def list_active_rooms(self) -> list[MeetingRoom]:
        return list(self.session.scalars(select(MeetingRoom).where(MeetingRoom.is_active.is_(True))).all())
