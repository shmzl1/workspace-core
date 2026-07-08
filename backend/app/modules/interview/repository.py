"""Interview repository database reads."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.interview.models import Interview, Interviewer, MeetingRoom


class InterviewRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_interviewers(self) -> list[Interviewer]:
        return list(self.session.scalars(select(Interviewer).where(Interviewer.is_active.is_(True)).order_by(Interviewer.id)))

    def list_meeting_rooms(self) -> list[MeetingRoom]:
        return list(self.session.scalars(select(MeetingRoom).where(MeetingRoom.is_active.is_(True)).order_by(MeetingRoom.id)))

    def list_interviews(self) -> list[Interview]:
        return list(self.session.scalars(select(Interview).order_by(Interview.start_at.desc()).limit(50)))
