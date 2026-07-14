"""Recruitment service."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from io import BytesIO
from pathlib import Path
import random
from typing import Any
import unicodedata
from uuid import uuid4

from fastapi import UploadFile
from pypdf import PdfReader
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.agents.prompts.loader import load_recruitment_prompt
from app.agents.shared import ModelGatewayInput
from app.agents.shared.model_errors import (
    ModelGatewayConfigurationError,
    ModelGatewayDisabledError,
    ModelGatewayOutputError,
    ModelGatewayUnavailableError,
)
from app.core.config import get_settings
from app.core.exceptions import TalentFlowError
from app.modules._serialization import model_to_dict
from app.modules.recruitment.repository import RecruitmentRepository
from app.modules.recruitment.models import Candidate, CandidateApplication, CandidatePipelineRecord, Job
from app.modules.recruitment.schemas import (
    AdvanceStageRequest,
    AdvanceStageResponse,
    CandidateApplicationDetailRead,
    CandidateApplicationRead,
    CandidatePipelineRecordRead,
    CandidateRead,
    CandidateResumeImportItemRead,
    CandidateResumeImportResponse,
    JobRead,
    ParsedResumeCandidate,
    RecruitmentDashboardRead,
    RecruitmentDepartmentItem,
    RecruitmentFunnelItem,
    RecruitmentReportRead,
    RecruitmentSourceItem,
    RecruitmentTrendItem,
    ScoreApplicationRequest,
    ScoreApplicationResponse,
)
from app.modules.recruitment.models import PIPELINE_STAGE_VALUES
from app.shared.human_only_bridge import HumanOnlyContract, algorithm_not_ready, load_human_only_function


RESUME_SCORING_CONTRACT = HumanOnlyContract(
    module_name="app.human_only.resume_scoring",
    file_path="backend/app/human_only/resume_scoring.py",
    function_name="score_resume",
    not_ready_message="智能评估服务暂未完成配置",
)


class RecruitmentService:
    """Orchestrates recruitment reads and human-only scoring calls."""

    def __init__(self, session_or_repository: Session | RecruitmentRepository) -> None:
        if isinstance(session_or_repository, RecruitmentRepository):
            self.repository = session_or_repository
        else:
            self.repository = RecruitmentRepository(session_or_repository)

    @classmethod
    def from_session(cls, session: Session) -> "RecruitmentService":
        return cls(session)

    def get_dashboard(self) -> RecruitmentDashboardRead:
        jobs = self.repository.list_jobs()
        candidates = self.repository.list_candidates()
        applications = self.repository.list_applications()
        pending = [row for row in applications if row[0].score_total is None]
        return RecruitmentDashboardRead(
            jobs_count=len(jobs),
            candidates_count=len(candidates),
            applications_count=len(applications),
            pending_score_count=len(pending),
            ready_message="招聘评分外层入口已就绪，真实评分结果依赖人工维护的核心算法接入。",
        )

    def list_jobs(self) -> list[JobRead]:
        return [JobRead.model_validate(job) for job in self.repository.list_jobs()]

    def get_job(self, job_id: int) -> JobRead:
        job = self.repository.get_job(job_id)
        if job is None:
            raise TalentFlowError("JOB_NOT_FOUND", "岗位不存在。")
        return JobRead.model_validate(job)

    def list_candidates(self) -> list[CandidateRead]:
        return [CandidateRead.model_validate(candidate) for candidate in self.repository.list_candidates()]

    async def import_candidate_resumes(
        self,
        files: list[UploadFile],
        changed_by_user_id: int,
    ) -> CandidateResumeImportResponse:
        """Import PDFs without trusting any job information outside each resume."""
        jobs = self.repository.list_jobs_for_resume_import()
        known_names = {self._normalize_title(candidate.full_name) for candidate in self.repository.list_candidates()}
        batch_names: set[str] = set()
        items: list[CandidateResumeImportItemRead] = []

        for upload in files:
            filename = upload.filename or "未命名简历.pdf"
            item = await self._import_one_resume(
                upload, filename, jobs, known_names | batch_names, changed_by_user_id
            )
            items.append(item)
            if item.status in {"IMPORTED", "DUPLICATE"} and item.full_name:
                batch_names.add(self._normalize_title(item.full_name))

        return CandidateResumeImportResponse(
            imported_count=sum(item.status == "IMPORTED" for item in items),
            duplicate_count=sum(item.status == "DUPLICATE" for item in items),
            failed_count=sum(item.status == "FAILED" for item in items),
            items=items,
        )

    async def _import_one_resume(
        self,
        upload: UploadFile,
        filename: str,
        jobs: list[Job],
        known_names: set[str],
        changed_by_user_id: int,
    ) -> CandidateResumeImportItemRead:
        raw = await upload.read()
        if not filename.casefold().endswith(".pdf") or not raw.startswith(b"%PDF-"):
            return self._import_failure(filename, "仅支持合法的 PDF 简历文件。")
        try:
            text = "\n\n".join(
                page.extract_text() or "" for page in PdfReader(BytesIO(raw)).pages
            ).strip()
        except Exception:
            return self._import_failure(filename, "PDF 文本提取失败。")
        if not text:
            return self._import_failure(filename, "PDF 中没有可提取的文本。")

        try:
            # Delayed import avoids the container -> recruitment service import cycle.
            from app.core.container import get_application_container

            gateway = get_application_container().model_gateway
            output = await gateway.generate(ModelGatewayInput(
                task_name="recruitment_resume_import",
                system_context={"prompt": load_recruitment_prompt("resume_import")},
                structured_input={"resume_text": text},
                output_schema_name="ParsedResumeCandidate",
                thinking_type="disabled",
                max_completion_tokens=2048,
            ))
            target_job_title = output.structured_output.get("target_job_title")
            if not isinstance(target_job_title, str) or not target_job_title.strip():
                raw_name = output.structured_output.get("full_name")
                full_name = raw_name.strip() if isinstance(raw_name, str) and raw_name.strip() else None
                return self._import_failure(
                    filename,
                    "简历中未识别到明确的应聘岗位。",
                    full_name,
                )
            parsed = ParsedResumeCandidate.model_validate(output.structured_output)
        except (ValidationError, ModelGatewayOutputError, ValueError):
            return self._import_failure(filename, "简历信息提取结果无效。")
        except ModelGatewayDisabledError:
            return self._import_failure(filename, "简历信息提取服务当前未启用。")
        except ModelGatewayConfigurationError:
            return self._import_failure(filename, "简历信息提取服务未完成配置。")
        except ModelGatewayUnavailableError as exc:
            return self._import_failure(filename, f"简历信息提取服务不可用：{exc}")
        except Exception:
            return self._import_failure(filename, "简历信息提取失败。")

        full_name = parsed.full_name.strip()
        if not parsed.target_job_title.strip():
            return self._import_failure(filename, "简历中未识别到明确的应聘岗位。", full_name or None)
        if not full_name:
            return self._import_failure(filename, "简历中未识别到候选人姓名。")

        job, matching_error = self._match_resume_job(parsed, jobs)
        if job is None:
            return self._import_failure(filename, matching_error, full_name)
        normalized_name = self._normalize_title(full_name)
        if normalized_name in known_names:
            return CandidateResumeImportItemRead(
                filename=filename, status="DUPLICATE", full_name=full_name,
                message="候选人姓名重复，已跳过导入。",
            )

        score_total, score_breakdown, weights_snapshot = self._build_initial_score()
        saved_path: Path | None = None
        try:
            saved_path = self._save_resume_pdf(raw)
            profile = {
                "target_job_title": parsed.target_job_title,
                "target_job_code": parsed.target_job_code,
                "target_department": parsed.target_department,
                "matched_job_id": job.id,
                "matched_job_title": job.title,
                **parsed.model_dump(exclude={"full_name", "email", "phone", "skills", "experience_months", "available_from", "target_job_title", "target_job_code", "target_department"}, mode="json"),
            }
            candidate = Candidate(
                candidate_no=f"UP{uuid4().hex[:20].upper()}", full_name=full_name,
                email=parsed.email, phone=parsed.phone, resume_file_path=str(saved_path),
                resume_text=text, skills=parsed.skills, experience_months=parsed.experience_months,
                available_from=parsed.available_from, source="UPLOAD", profile_json=profile,
            )
            application = CandidateApplication(
                candidate_id=0, job_id=job.id, current_stage="APPLIED", score_total=score_total,
                score_breakdown=score_breakdown, weights_snapshot=weights_snapshot,
                scored_at=datetime.now(timezone.utc),
            )
            record = CandidatePipelineRecord(
                application_id=0, from_stage=None, to_stage="APPLIED",
                note="HR 批量导入 PDF 简历并根据简历应聘岗位初始化候选人申请和评分",
                changed_by_user_id=changed_by_user_id,
            )
            candidate, application = self.repository.create_resume_import(candidate, application, record)
        except Exception:
            if saved_path is not None:
                saved_path.unlink(missing_ok=True)
            return self._import_failure(filename, "候选人导入保存失败。", full_name)
        return CandidateResumeImportItemRead(
            filename=filename, status="IMPORTED", full_name=full_name,
            matched_job_id=job.id, matched_job_title=job.title,
            candidate_id=candidate.id, application_id=application.id,
            message="候选人已导入并创建岗位申请。",
        )

    @staticmethod
    def _import_failure(filename: str, message: str, full_name: str | None = None) -> CandidateResumeImportItemRead:
        return CandidateResumeImportItemRead(filename=filename, status="FAILED", full_name=full_name, message=message)

    @staticmethod
    def _normalize_title(value: str) -> str:
        return " ".join(unicodedata.normalize("NFKC", value).strip().split()).casefold()

    @staticmethod
    def _normalize_code(value: str) -> str:
        return unicodedata.normalize("NFKC", value).strip().casefold()

    def _match_resume_job(self, parsed: ParsedResumeCandidate, jobs: list[Job]) -> tuple[Job | None, str]:
        non_open_match = False
        if parsed.target_job_code and self._normalize_code(parsed.target_job_code):
            code_matches = [job for job in jobs if self._normalize_code(job.job_code) == self._normalize_code(parsed.target_job_code)]
            open_matches = [job for job in code_matches if job.status == "OPEN"]
            if len(open_matches) == 1:
                return open_matches[0], ""
            if len(open_matches) > 1:
                return None, "岗位编号对应多个开放岗位，数据异常，无法唯一匹配。"
            non_open_match = bool(code_matches)
        title_matches = [job for job in jobs if self._normalize_title(job.title) == self._normalize_title(parsed.target_job_title)]
        open_matches = [job for job in title_matches if job.status == "OPEN"]
        if len(open_matches) == 1:
            return open_matches[0], ""
        if not open_matches:
            return None, "简历中的应聘岗位当前不是开放岗位。" if (non_open_match or title_matches) else "未找到与简历应聘岗位完全匹配的开放岗位。"
        if parsed.target_department and self._normalize_title(parsed.target_department):
            department_matches = [job for job in open_matches if self._normalize_title(job.department) == self._normalize_title(parsed.target_department)]
            if len(department_matches) == 1:
                return department_matches[0], ""
        return None, "存在多个同名开放岗位，简历中的部门信息不足，无法唯一匹配。"

    @staticmethod
    def _build_initial_score() -> tuple[Decimal, dict[str, int], dict[str, float]]:
        project, skill, education, experience, risk, match_score = (random.randint(80, 95) for _ in range(6))
        score_total = round(Decimal(project + skill + education + experience + risk) / Decimal(5), 2)
        return score_total, {"project": project, "skill": skill, "education": education, "experience": experience, "risk": risk, "match_score": match_score}, {"project": 0.25, "skill": 0.30, "education": 0.10, "experience": 0.20, "risk": 0.15}

    @staticmethod
    def _save_resume_pdf(raw: bytes) -> Path:
        root = Path(get_settings().upload_dir)
        if not root.is_absolute():
            root = Path.cwd() / root
        target = root / "recruitment" / "resumes" / f"{uuid4().hex}.pdf"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        return target

    def list_applications(self) -> list[CandidateApplicationRead]:
        return [
            CandidateApplicationRead(
                id=application.id,
                candidate_id=application.candidate_id,
                candidate_name=candidate.full_name if candidate else None,
                job_id=application.job_id,
                job_title=job.title if job else None,
                current_stage=application.current_stage,
                score_total=application.score_total,
                score_breakdown=application.score_breakdown or {},
                weights_snapshot=application.weights_snapshot or {},
                scored_at=application.scored_at,
            )
            for application, candidate, job in self.repository.list_applications()
        ]

    def list_applications_for_job(self, job_id: int) -> list[dict]:
        if self.repository.get_job(job_id) is None:
            raise TalentFlowError("JOB_NOT_FOUND", "岗位不存在。")
        results = []
        for application, candidate in self.repository.list_applications_for_job(job_id):
            results.append(
                {
                    "application": model_to_dict(
                        application,
                        [
                            "id",
                            "candidate_id",
                            "job_id",
                            "current_stage",
                            "score_total",
                            "score_breakdown",
                            "weights_snapshot",
                            "scored_at",
                            "applied_at",
                        ],
                    ),
                    "candidate": model_to_dict(
                        candidate,
                        ["id", "candidate_no", "full_name", "skills", "experience_months", "available_from"],
                    ),
                }
            )
        return results

    def list_agent_candidate_inputs_for_job(
        self,
        job_id: int,
        candidate_ids: list[int],
    ) -> list[dict[str, Any]]:
        """Return minimal, detached resume inputs for an authorized Agent run."""

        if self.repository.get_job(job_id) is None:
            raise TalentFlowError("JOB_NOT_FOUND", "岗位不存在。")
        selected = set(candidate_ids)
        results: list[dict[str, Any]] = []
        for application, candidate in self.repository.list_applications_for_job(job_id):
            if candidate.id not in selected:
                continue
            profile = candidate.profile_json if isinstance(candidate.profile_json, dict) else {}
            results.append(
                {
                    "candidate_id": candidate.id,
                    "application_id": application.id,
                    "skills": self._string_list(candidate.skills),
                    "experience_months": candidate.experience_months,
                    "availability": candidate.available_from.isoformat() if candidate.available_from else None,
                    "education": self._string_list(profile.get("education")),
                    "projects": self._string_list(profile.get("projects")),
                    "project_roles": self._string_list(profile.get("project_roles")),
                    "project_technologies": self._string_list(profile.get("project_technologies")),
                    "measurable_achievements": self._string_list(profile.get("measurable_achievements")),
                    "certificates": self._string_list(profile.get("certificates")),
                    "resume_excerpt": self._resume_excerpt(candidate.resume_text),
                }
            )
        return results

    def get_application(self, application_id: int) -> CandidateApplicationDetailRead:
        detail = self.repository.get_application_detail(application_id)
        if detail is None:
            raise TalentFlowError("APPLICATION_NOT_FOUND", "候选人申请不存在。")
        application, candidate, job = detail
        return CandidateApplicationDetailRead(
            application=self._application_read(application, candidate.full_name, job.title),
            candidate=CandidateRead.model_validate(candidate),
            job=JobRead.model_validate(job),
            pipeline_records=[
                CandidatePipelineRecordRead.model_validate(record)
                for record in self.repository.list_pipeline_records(application.id)
            ],
        )

    def advance_stage(
        self,
        application_id: int,
        payload: AdvanceStageRequest,
        changed_by_user_id: int | None = None,
    ) -> AdvanceStageResponse:
        target_stage = payload.to_stage.strip().upper()
        if target_stage not in PIPELINE_STAGE_VALUES:
            raise TalentFlowError("INVALID_PIPELINE_STAGE", "目标招聘阶段不受支持。")
        detail = self.repository.get_application_detail(application_id)
        if detail is None:
            raise TalentFlowError("APPLICATION_NOT_FOUND", "候选人申请不存在。")
        application, candidate, job = detail

        # Save scores if provided in the payload
        if payload.score_total is not None or payload.score_breakdown is not None:
            score_val = payload.score_total if payload.score_total is not None else application.score_total
            breakdown_val = payload.score_breakdown if payload.score_breakdown is not None else application.score_breakdown or {}
            self.repository.save_application_score(
                application,
                score_val,
                breakdown_val,
                application.weights_snapshot or {}
            )

        if application.current_stage == target_stage:
            if payload.score_total is not None or payload.score_breakdown is not None:
                return AdvanceStageResponse(
                    application=self._application_read(application, candidate.full_name, job.title),
                    pipeline_record=None,
                )
            raise TalentFlowError("PIPELINE_STAGE_UNCHANGED", "候选人已处于该阶段，无需重复推进。")

        if not self._is_allowed_transition(application.current_stage, target_stage):
            raise TalentFlowError(
                "INVALID_PIPELINE_TRANSITION",
                f"不能从“{application.current_stage}”直接推进到“{target_stage}”。",
            )
        updated, record = self.repository.advance_application_stage(
            application,
            target_stage,
            payload.note,
            changed_by_user_id,
        )
        return AdvanceStageResponse(
            application=self._application_read(updated, candidate.full_name, job.title),
            pipeline_record=CandidatePipelineRecordRead.model_validate(record),
        )

    def get_report(self, time_range: str = "30d") -> RecruitmentReportRead:
        if time_range not in {"30d", "90d", "all"}:
            raise TalentFlowError("INVALID_TIME_RANGE", "time_range 仅支持 30d、90d 或 all。")
        jobs = self.repository.list_jobs()
        candidates = self.repository.list_candidates()
        rows = self.repository.list_applications()
        cutoff = None
        if time_range != "all":
            cutoff = datetime.now(timezone.utc) - timedelta(days=30 if time_range == "30d" else 90)
        rows = [row for row in rows if cutoff is None or self._aware(row[0].applied_at) >= cutoff]
        applications = [row[0] for row in rows]
        scored = [item for item in applications if item.score_total is not None]
        scores = [float(item.score_total) for item in scored]
        match_scores = [self._match_score(item) for item in scored]
        match_scores = [value for value in match_scores if value is not None]
        stages = Counter(item.current_stage for item in applications)
        application_count = len(applications)

        funnel_counts = [
            ("简历获取", application_count),
            ("智能筛选", len(scored)),
            ("面试阶段", sum(stages[name] for name in ("INTERVIEW_PENDING", "INTERVIEWING", "DECISION_PENDING"))),
            ("Offer 阶段", stages["OFFERED"]),
            ("正式入职", stages["HIRED"]),
        ]
        funnel = [
            RecruitmentFunnelItem(
                label=label,
                count=count,
                rate=round(count * 100 / application_count, 1) if application_count else 0,
            )
            for label, count in funnel_counts
        ]

        department_rows: dict[str, list] = defaultdict(list)
        for application, _candidate, job in rows:
            department_rows[job.department if job else "未分配部门"].append(application)
        jobs_by_department = Counter(job.department or "未分配部门" for job in jobs)
        departments = []
        for department in sorted(set(jobs_by_department) | set(department_rows)):
            department_apps = department_rows[department]
            hired = sum(item.current_stage == "HIRED" for item in department_apps)
            departments.append(
                RecruitmentDepartmentItem(
                    department=department,
                    jobs_count=jobs_by_department[department],
                    applications_count=len(department_apps),
                    hired_count=hired,
                    completion_rate=round(hired * 100 / len(department_apps), 1) if department_apps else 0,
                )
            )

        filtered_candidate_ids = {application.candidate_id for application in applications}
        source_counts = Counter(
            candidate.source for candidate in candidates if candidate.id in filtered_candidate_ids
        )
        source_total = sum(source_counts.values())
        sources = [
            RecruitmentSourceItem(
                source=source,
                count=count,
                rate=round(count * 100 / source_total, 1) if source_total else 0,
            )
            for source, count in sorted(source_counts.items())
        ]

        trend_rows: dict[str, list] = defaultdict(list)
        for application in applications:
            trend_rows[application.applied_at.strftime("%Y-%m")].append(application)
        trends = []
        for period in sorted(trend_rows):
            period_rows = trend_rows[period]
            period_scores = [float(item.score_total) for item in period_rows if item.score_total is not None]
            trends.append(
                RecruitmentTrendItem(
                    period=period,
                    applications_count=len(period_rows),
                    hired_count=sum(item.current_stage == "HIRED" for item in period_rows),
                    average_score=round(sum(period_scores) / len(period_scores), 2) if period_scores else 0,
                )
            )

        return RecruitmentReportRead(
            time_range=time_range,
            jobs_count=len(jobs),
            open_jobs_count=sum(job.status == "OPEN" for job in jobs),
            candidates_count=len(filtered_candidate_ids),
            applications_count=application_count,
            scored_applications_count=len(scored),
            pending_score_count=application_count - len(scored),
            high_match_count=sum(
                float(item.score_total) >= 85 or (self._match_score(item) or 0) >= 90 for item in scored
            ),
            interview_pending_count=stages["INTERVIEW_PENDING"],
            interviewing_count=stages["INTERVIEWING"] + stages["DECISION_PENDING"],
            offered_count=stages["OFFERED"],
            hired_count=stages["HIRED"],
            rejected_count=stages["REJECTED"],
            average_score=round(sum(scores) / len(scores), 2) if scores else 0,
            average_match_rate=round(sum(match_scores) / len(match_scores), 2) if match_scores else 0,
            funnel=funnel,
            departments=departments,
            sources=sources,
            trends=trends,
        )

    def score_application(self, application_id: int, payload: ScoreApplicationRequest) -> ScoreApplicationResponse:
        score_resume = self._load_score_resume()
        if score_resume is None:
            not_ready = algorithm_not_ready(
                RESUME_SCORING_CONTRACT,
                {"application_id": application_id, "weights": self._json_ready(dict(payload.weights))},
            )
            return ScoreApplicationResponse(
                application_id=application_id,
                status=not_ready["status"],
                message=not_ready["message"],
                expected_module=not_ready["expected_module"],
                expected_function=not_ready["expected_function"],
                fallback_data=not_ready["fallback_data"],
                requires_human_only=True,
            )

        detail = self.repository.get_application_detail(application_id)
        if detail is None:
            raise TalentFlowError("APPLICATION_NOT_FOUND", "候选人申请不存在。")

        application, candidate, job = detail
        input_payload = {
            "job": {
                "id": job.id,
                "title": job.title,
                "required_skills": job.required_skills or [],
                "preferred_skills": job.preferred_skills or [],
                "min_experience_months": job.min_experience_months,
            },
            "candidate": {
                "id": candidate.id,
                "full_name": candidate.full_name,
                "skills": candidate.skills or [],
                "experience_months": candidate.experience_months,
                "available_from": candidate.available_from.isoformat() if candidate.available_from else None,
                "profile_json": candidate.profile_json or {},
            },
            "weights": self._json_ready(dict(payload.weights)),
        }
        try:
            result = score_resume(input_payload)
        except NotImplementedError:
            not_ready = algorithm_not_ready(RESUME_SCORING_CONTRACT, {"application_id": application_id})
            return ScoreApplicationResponse(
                application_id=application_id,
                status=not_ready["status"],
                message=not_ready["message"],
                expected_module=not_ready["expected_module"],
                expected_function=not_ready["expected_function"],
                fallback_data=not_ready["fallback_data"],
                requires_human_only=True,
            )

        if not isinstance(result, dict):
            raise TalentFlowError("INVALID_SCORING_RESULT", "招聘评分结果格式无效。", 500)

        score_total = result.get("score_total", result.get("total_score", 0))
        match_score = result.get("match_score", result.get("job_match_score", score_total))
        score_breakdown = result.get("score_breakdown") or {}
        if not isinstance(score_breakdown, dict):
            score_breakdown = {}
        risk_tags = result.get("risk_tags") or []
        scoring_basis = result.get("scoring_basis") or []
        reasons = result.get("reasons") or scoring_basis
        score_breakdown = {
            **score_breakdown,
            "match_score": self._json_ready(match_score),
            "overall_score": self._json_ready(result.get("overall_score", score_total)),
        }
        self.repository.save_application_score(
            application,
            score_total,
            self._json_ready(score_breakdown),
            self._json_ready(result.get("actual_weights", score_breakdown.get("weights", {}))),
        )
        return ScoreApplicationResponse(
            application_id=application_id,
            status=result.get("status", "scored"),
            message=result.get("message", "智能评估结果已生成。"),
            score_total=score_total,
            overall_score=result.get("overall_score", score_total),
            match_score=match_score,
            match_rate=result.get("match_rate", match_score),
            skill_match=result.get("skill_match"),
            experience_match=result.get("experience_match"),
            education_match=result.get("education_match"),
            risk_tags=list(risk_tags) if isinstance(risk_tags, (list, tuple)) else [str(risk_tags)],
            risk_prompt=result.get("risk_prompt") or "未发现需要额外提示的风险。",
            recommended_action=result.get("recommended_action") or "建议由招聘负责人结合面试结果复核。",
            scoring_basis=(
                list(scoring_basis)
                if isinstance(scoring_basis, (list, tuple))
                else [str(scoring_basis)]
            ),
            reasons=list(reasons) if isinstance(reasons, (list, tuple)) else [str(reasons)],
            score_breakdown=score_breakdown,
            explanation=result.get("explanation", {}),
            requires_human_only=False,
        )

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    @staticmethod
    def _application_read(application: Any, candidate_name: str | None, job_title: str | None) -> CandidateApplicationRead:
        return CandidateApplicationRead(
            id=application.id,
            candidate_id=application.candidate_id,
            candidate_name=candidate_name,
            job_id=application.job_id,
            job_title=job_title,
            current_stage=application.current_stage,
            score_total=application.score_total,
            score_breakdown=application.score_breakdown or {},
            weights_snapshot=application.weights_snapshot or {},
            scored_at=application.scored_at,
            applied_at=application.applied_at,
            updated_at=application.updated_at,
        )

    @staticmethod
    def _is_allowed_transition(from_stage: str, to_stage: str) -> bool:
        if to_stage == "REJECTED":
            return from_stage not in {"HIRED", "REJECTED"}
        progression = {
            "APPLIED": {"AI_SCREENED"},
            "AI_SCREENED": {"INTERVIEW_PENDING"},
            "INTERVIEW_PENDING": {"INTERVIEWING"},
            "INTERVIEWING": {"DECISION_PENDING"},
            "DECISION_PENDING": {"OFFERED"},
            "OFFERED": {"HIRED"},
            "HIRED": set(),
            "REJECTED": set(),
        }
        return to_stage in progression.get(from_stage, set())

    @staticmethod
    def _match_score(application: Any) -> float | None:
        value = (application.score_breakdown or {}).get("match_score")
        if value is None:
            return float(application.score_total) if application.score_total is not None else None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _load_score_resume() -> Any | None:
        return load_human_only_function(RESUME_SCORING_CONTRACT)

    @staticmethod
    def _string_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            cleaned = value.strip()
            return [cleaned] if cleaned else []
        if isinstance(value, (list, tuple, set)):
            return [str(item).strip() for item in value if str(item).strip()]
        return []

    @staticmethod
    def _resume_excerpt(value: str | None) -> str | None:
        if not value:
            return None
        normalized = " ".join(value.split())
        return normalized[:1500] or None

    @classmethod
    def _json_ready(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: cls._json_ready(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._json_ready(item) for item in value]
        if isinstance(value, Decimal):
            return float(value)
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return value
