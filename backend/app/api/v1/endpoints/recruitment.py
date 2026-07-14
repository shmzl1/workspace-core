"""Recruitment route boundary."""

from io import BytesIO
import os
from fastapi import APIRouter, Depends, File, UploadFile, Response
from fastapi.responses import FileResponse
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import require_any_permission, require_permission
from app.core.exceptions import TalentFlowError
from app.modules.recruitment.models import Candidate
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


@router.get("/applications/{application_id}/resume")
def get_candidate_resume(
    application_id: int,
    _=Depends(require_any_permission("recruitment.read", "candidate.read")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    app_detail = service.get_application(application_id)
    candidate = service.repository.session.get(Candidate, app_detail.candidate.id)
    if candidate is None:
        raise TalentFlowError("RESUME_NOT_FOUND", "未找到该候选人的简历信息。")
    
    # 1. If physical PDF exists, serve it
    if candidate.resume_file_path and os.path.exists(candidate.resume_file_path):
        filename = f"{candidate.full_name}_简历.pdf"
        return FileResponse(
            candidate.resume_file_path,
            media_type="application/pdf",
            filename=filename,
        )
    
    # 2. Otherwise fallback to candidate.resume_text served as plain text
    if candidate.resume_text:
        text_content = f"候选人姓名：{candidate.full_name}\n\n简历文本内容：\n\n{candidate.resume_text}"
        return Response(
            content=text_content.encode("utf-8"),
            media_type="text/plain; charset=utf-8",
            headers={
                "Content-Disposition": f"inline; filename={candidate.full_name}_resume.txt"
            }
        )
        
    raise TalentFlowError("RESUME_EMPTY", "该候选人简历内容为空。")




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


@router.post("/candidates/{candidate_id}/resume")
async def upload_candidate_resume(
    candidate_id: int,
    file: UploadFile = File(...),
    _=Depends(require_permission("recruitment.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
) -> object:
    candidate = service.repository.session.get(Candidate, candidate_id)
    if candidate is None:
        raise TalentFlowError("CANDIDATE_NOT_FOUND", "候选人不存在。")
    
    filename = file.filename or "简历.pdf"
    raw = await file.read()
    if not filename.casefold().endswith(".pdf") or not raw.startswith(b"%PDF-"):
        raise TalentFlowError("INVALID_FILE", "仅支持合法的 PDF 简历文件。")
        
    try:
        text = "\n\n".join(
            page.extract_text() or "" for page in PdfReader(BytesIO(raw)).pages
        ).strip()
    except Exception:
        raise TalentFlowError("PDF_PARSE_FAILED", "PDF 文本提取失败。")
        
    saved_path = service._save_resume_pdf(raw)
    
    try:
        candidate.resume_file_path = str(saved_path)
        candidate.resume_text = text
        service.repository.session.commit()
    except Exception:
        service.repository.session.rollback()
        saved_path.unlink(missing_ok=True)
        raise TalentFlowError("SAVE_FAILED", "保存简历信息失败。")
        
    return ok({"message": "简历上传成功。", "candidate_id": candidate_id})

