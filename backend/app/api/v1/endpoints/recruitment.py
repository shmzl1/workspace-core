"""Recruitment route boundary."""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import require_any_permission, require_permission
from app.modules.recruitment.schemas import AdvanceStageRequest, ScoreApplicationRequest
from app.modules.recruitment.service import RecruitmentService
from app.shared.response import ok

router = APIRouter()


def get_recruitment_service(session: Session = Depends(get_db_session)) -> RecruitmentService:
    return RecruitmentService(session)


@router.get("/dashboard")
def get_recruitment_dashboard(_=Depends(require_permission("recruitment.read")), service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.get_dashboard())


@router.get("/jobs")
def list_jobs(_=Depends(require_permission("recruitment.read")), service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_jobs())


@router.get("/jobs/{job_id}")
def get_job(job_id: int, _=Depends(require_permission("recruitment.read")), service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.get_job(job_id))


@router.get("/candidates")
def list_candidates(_=Depends(require_permission("candidate.read")), service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_candidates())


@router.post("/candidates/import")
async def import_candidate_resumes(
    files: list[UploadFile] = File(...),
    current_user=Depends(require_permission("recruitment.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
) -> object:
    return ok(await service.import_candidate_resumes(files, current_user.id))


@router.get("/applications")
def list_applications(_=Depends(require_any_permission("recruitment.read", "candidate.read")), service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_applications())


@router.get("/applications/{application_id}")
def get_application(application_id: int, _=Depends(require_any_permission("recruitment.read", "candidate.read")), service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.get_application(application_id))


@router.get("/report")
def get_recruitment_report(
    time_range: str = "30d",
    _=Depends(require_permission("reporting.recruitment.read")),
    service: RecruitmentService = Depends(get_recruitment_service),
) -> object:
    return ok(service.get_report(time_range))


@router.get("/jobs/{job_id}/applications")
def list_job_applications(job_id: int, _=Depends(require_any_permission("recruitment.read", "candidate.read")), service: RecruitmentService = Depends(get_recruitment_service)) -> object:
    return ok(service.list_applications_for_job(job_id))


@router.post("/applications/{application_id}/score")
def score_application(
    application_id: int,
    payload: ScoreApplicationRequest,
    _=Depends(require_permission("candidate.score")),
    service: RecruitmentService = Depends(get_recruitment_service),
) -> object:
    return ok(service.score_application(application_id, payload))


@router.post("/applications/{application_id}/advance")
def advance_application_stage(
    application_id: int,
    payload: AdvanceStageRequest,
    _=Depends(require_permission("candidate.stage.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
) -> object:
    return ok(service.advance_stage(application_id, payload))
