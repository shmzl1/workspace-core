"""Recruitment route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.recruitment.service import RecruitmentService
from app.shared.response import ok

router = APIRouter()


def get_recruitment_service(session: Session = Depends(get_db_session)) -> RecruitmentService:
    return RecruitmentService.from_session(session)


@router.get("/jobs")
def list_jobs(service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_jobs())


@router.get("/candidates")
def list_candidates(service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_candidates())


@router.get("/jobs/{job_id}/applications")
def list_job_applications(job_id: int, service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_applications_for_job(job_id))
