"""Recruitment route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.recruitment.schemas import ScoreApplicationRequest
from app.modules.recruitment.service import RecruitmentService
from app.shared.response import ok
from app.shared.trace import get_trace_id

router = APIRouter()


@router.get("/dashboard")
def get_recruitment_dashboard(session: Session = Depends(get_db_session)) -> object:
    service = RecruitmentService(session)
    return ok(service.get_dashboard(), get_trace_id())


@router.get("/jobs")
def list_jobs(session: Session = Depends(get_db_session)) -> object:
    service = RecruitmentService(session)
    return ok(service.list_jobs(), get_trace_id())


@router.get("/candidates")
def list_candidates(session: Session = Depends(get_db_session)) -> object:
    service = RecruitmentService(session)
    return ok(service.list_candidates(), get_trace_id())


@router.get("/applications")
def list_applications(session: Session = Depends(get_db_session)) -> object:
    service = RecruitmentService(session)
    return ok(service.list_applications(), get_trace_id())


@router.post("/applications/{application_id}/score")
def score_application(
    application_id: int,
    payload: ScoreApplicationRequest,
    session: Session = Depends(get_db_session),
) -> object:
    service = RecruitmentService(session)
    return ok(service.score_application(application_id, payload), get_trace_id())
