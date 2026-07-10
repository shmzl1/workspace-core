"""Interview route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.modules.interview.schemas import ConfirmScheduleRequest, SchedulePreviewRequest
from app.modules.interview.service import InterviewService
from app.shared.response import ok

router = APIRouter()


def get_interview_service(session: Session = Depends(get_db_session)) -> InterviewService:
    return InterviewService.from_session(session)


@router.post("/schedule/preview")
def preview_schedule(
    payload: SchedulePreviewRequest,
    _=Depends(require_permission("interview.manage")),
    service: InterviewService = Depends(get_interview_service),
) -> object:
    return ok(service.preview_schedule(payload))


@router.post("/schedule/confirm")
def confirm_schedule(
    payload: ConfirmScheduleRequest,
    _=Depends(require_permission("interview.manage")),
    service: InterviewService = Depends(get_interview_service),
) -> object:
    return ok(service.confirm_schedule(payload))


@router.get("/interviewers")
def list_interviewers(_=Depends(require_permission("interview.read")), service: InterviewService = Depends(get_interview_service)) -> object:
    return ok(service.list_interviewers())


@router.get("/meeting-rooms")
def list_meeting_rooms(_=Depends(require_permission("interview.read")), service: InterviewService = Depends(get_interview_service)) -> object:
    return ok(service.list_meeting_rooms())


@router.get("")
def list_interviews(_=Depends(require_permission("interview.read")), service: InterviewService = Depends(get_interview_service)) -> object:
    return ok(service.list_interviews())
