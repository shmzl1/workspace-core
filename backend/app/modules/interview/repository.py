"""Interview repository."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.employee.models import Employee
from app.modules.interview.models import Interview, Interviewer, InterviewSlot, MeetingRoom
from app.modules.recruitment.models import Candidate, CandidateApplication, Job


class InterviewRepository:
    """Database reads and writes for interview scheduling."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_application_detail(self, application_id: int) -> tuple[CandidateApplication, Candidate, Job] | None:
        row = self.session.execute(
            select(CandidateApplication, Candidate, Job)
            .join(Candidate, Candidate.id == CandidateApplication.candidate_id)
            .join(Job, Job.id == CandidateApplication.job_id)
            .where(CandidateApplication.id == application_id)
        ).one_or_none()
        return tuple(row) if row is not None else None

    def list_interviewers_with_employees(self) -> list[tuple[Interviewer, Employee | None]]:
        rows = self.session.execute(
            select(Interviewer, Employee)
            .join(Employee, Employee.id == Interviewer.employee_id, isouter=True)
            .where(Interviewer.is_active.is_(True))
            .order_by(Interviewer.id)
        )
        return [(interviewer, employee) for interviewer, employee in rows.all()]

    def get_interviewer_with_employee(self, interviewer_id: int) -> tuple[Interviewer, Employee | None] | None:
        return self.session.execute(
            select(Interviewer, Employee)
            .join(Employee, Employee.id == Interviewer.employee_id, isouter=True)
            .where(Interviewer.id == interviewer_id, Interviewer.is_active.is_(True))
        ).one_or_none()

    def list_meeting_rooms(self) -> list[MeetingRoom]:
        return list(
            self.session.scalars(
                select(MeetingRoom).where(MeetingRoom.is_active.is_(True)).order_by(MeetingRoom.id)
            ).all()
        )

    def get_meeting_room(self, room_id: int) -> MeetingRoom | None:
        return self.session.scalar(
            select(MeetingRoom).where(MeetingRoom.id == room_id, MeetingRoom.is_active.is_(True))
        )

    def list_interviews(self) -> list[Interview]:
        return list(self.session.scalars(select(Interview).order_by(Interview.start_at.desc()).limit(100)).all())

    def list_scheduled_interviews_with_applications(self) -> list[tuple[Interview, CandidateApplication]]:
        rows = self.session.execute(
            select(Interview, CandidateApplication)
            .join(CandidateApplication, CandidateApplication.id == Interview.application_id)
            .where(Interview.status == "SCHEDULED")
            .order_by(Interview.start_at)
        )
        return [(interview, application) for interview, application in rows.all()]

    def list_candidate_slots(self, candidate_id: int, *, ends_after: datetime | None = None) -> list[InterviewSlot]:
        return self._list_slots(InterviewSlot.candidate_id == candidate_id, ends_after=ends_after)

    def list_interviewer_slots(self, interviewer_id: int, *, ends_after: datetime | None = None) -> list[InterviewSlot]:
        return self._list_slots(InterviewSlot.interviewer_id == interviewer_id, ends_after=ends_after)

    def list_room_slots(self, room_id: int, *, ends_after: datetime | None = None) -> list[InterviewSlot]:
        return self._list_slots(InterviewSlot.meeting_room_id == room_id, ends_after=ends_after)

    def resource_has_available_slot(
        self,
        *,
        candidate_id: int,
        interviewer_id: int,
        room_id: int,
        start_at: datetime,
        end_at: datetime,
    ) -> bool:
        return all((
            self._has_slot(InterviewSlot.candidate_id == candidate_id, start_at, end_at),
            self._has_slot(InterviewSlot.interviewer_id == interviewer_id, start_at, end_at),
            self._has_slot(InterviewSlot.meeting_room_id == room_id, start_at, end_at),
        ))

    def find_conflicts(
        self,
        *,
        candidate_id: int,
        interviewer_id: int,
        room_id: int,
        start_at: datetime,
        end_at: datetime,
    ) -> list[dict[str, object]]:
        conflicts: list[dict[str, object]] = []
        for interview, application in self.list_scheduled_interviews_with_applications():
            if not (start_at < interview.end_at and end_at > interview.start_at):
                continue
            affected: list[str] = []
            if application.candidate_id == candidate_id:
                affected.append("候选人")
            if interview.interviewer_id == interviewer_id:
                affected.append("面试官")
            if interview.meeting_room_id == room_id:
                affected.append("会议室")
            if affected:
                conflicts.append({
                    "interview_id": interview.id,
                    "resources": affected,
                    "start_at": interview.start_at.isoformat(),
                    "end_at": interview.end_at.isoformat(),
                })
        return conflicts

    def save_interview(
        self,
        *,
        application_id: int,
        interviewer_id: int,
        room_id: int,
        start_at: datetime,
        end_at: datetime,
        conflict_explanation: dict[str, object],
    ) -> Interview:
        interview = Interview(
            application_id=application_id,
            interviewer_id=interviewer_id,
            meeting_room_id=room_id,
            start_at=start_at,
            end_at=end_at,
            status="SCHEDULED",
            conflict_explanation=conflict_explanation,
        )
        self.session.add(interview)
        self.session.commit()
        self.session.refresh(interview)
        return interview

    def _list_slots(self, resource_clause: object, *, ends_after: datetime | None = None) -> list[InterviewSlot]:
        clauses = [resource_clause, InterviewSlot.is_available.is_(True)]
        if ends_after is not None:
            clauses.append(InterviewSlot.end_at > ends_after)
        return list(
            self.session.scalars(
                select(InterviewSlot)
                .where(*clauses)
                .order_by(InterviewSlot.start_at)
            ).all()
        )

    def _has_slot(self, resource_clause: object, start_at: datetime, end_at: datetime) -> bool:
        return self.session.scalar(
            select(InterviewSlot.id).where(
                resource_clause,
                InterviewSlot.is_available.is_(True),
                InterviewSlot.start_at <= start_at,
                InterviewSlot.end_at >= end_at,
            )
        ) is not None
