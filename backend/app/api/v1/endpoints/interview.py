"""Interview route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.interview.service import InterviewService
from app.shared.response import ok

router = APIRouter()


def get_interview_service(session: Session = Depends(get_db_session)) -> InterviewService:
    return InterviewService.from_session(session)


@router.get("/interviewers")
def list_interviewers(service: InterviewService = Depends(get_interview_service)) -> object:
    return ok(service.list_interviewers())


@router.get("/meeting-rooms")
def list_meeting_rooms(service: InterviewService = Depends(get_interview_service)) -> object:
    return ok(service.list_meeting_rooms())


@router.get("")
def list_interviews(service: InterviewService = Depends(get_interview_service)) -> object:
    return ok(service.list_interviews())
