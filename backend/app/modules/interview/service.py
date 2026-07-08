"""Interview service read boundary."""

from app.modules._serialization import model_to_dict
from app.modules.interview.repository import InterviewRepository
from sqlalchemy.orm import Session


class InterviewService:
    def __init__(self, repository: InterviewRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: Session) -> "InterviewService":
        return cls(InterviewRepository(session))

    def list_interviewers(self) -> list[dict]:
        return [
            model_to_dict(interviewer, ["id", "employee_id", "specialties", "max_interviews_per_day", "is_active"])
            for interviewer in self.repository.list_interviewers()
        ]

    def list_meeting_rooms(self) -> list[dict]:
        return [
            model_to_dict(room, ["id", "room_code", "name", "location", "capacity", "is_active"])
            for room in self.repository.list_meeting_rooms()
        ]

    def list_interviews(self) -> list[dict]:
        return [
            model_to_dict(
                interview,
                [
                    "id",
                    "application_id",
                    "interviewer_id",
                    "meeting_room_id",
                    "start_at",
                    "end_at",
                    "status",
                    "conflict_explanation",
                    "created_by_user_id",
                ],
            )
            for interview in self.repository.list_interviews()
        ]
