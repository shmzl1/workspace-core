"""Recruitment route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.recruitment.schemas import ScoreApplicationRequest
from app.modules.recruitment.service import RecruitmentService
from app.shared.response import ok

router = APIRouter()


def get_recruitment_service(session: Session = Depends(get_db_session)) -> RecruitmentService:
    return RecruitmentService(session)


@router.get("/dashboard")
def get_recruitment_dashboard(service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.get_dashboard())


@router.get("/jobs")
def list_jobs(service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_jobs())


@router.get("/candidates")
def list_candidates(service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_candidates())


@router.get("/applications")
def list_applications(service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_applications())


@router.get("/report")
def get_recruitment_report(
    time_range: str = "30d",
    service: RecruitmentService = Depends(get_recruitment_service),
) -> object:
    return ok(service.get_report(time_range))


@router.get("/jobs/{job_id}/applications")
def list_job_applications(job_id: int, service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_applications_for_job(job_id))


@router.post("/applications/{application_id}/score")
def score_application(
    application_id: int,
    payload: ScoreApplicationRequest,
    service: RecruitmentService = Depends(get_recruitment_service),
) -> object:
    return ok(service.score_application(application_id, payload))
