"""Interview route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.interview.schemas import SchedulePreviewRequest
from app.modules.interview.service import InterviewService
from app.shared.response import ok
from app.shared.trace import get_trace_id

router = APIRouter()


@router.post("/schedule/preview")
def preview_schedule(
    payload: SchedulePreviewRequest,
    session: Session = Depends(get_db_session),
) -> object:
    service = InterviewService(session)
    return ok(service.preview_schedule(payload), get_trace_id())
