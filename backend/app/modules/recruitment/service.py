"""Recruitment service."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules._serialization import model_to_dict
from app.modules.recruitment.repository import RecruitmentRepository
from app.modules.recruitment.schemas import (
    AdvanceStageRequest,
    AdvanceStageResponse,
    CandidateApplicationDetailRead,
    CandidateApplicationRead,
    CandidatePipelineRecordRead,
    CandidateRead,
    JobRead,
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
        if application.current_stage == target_stage:
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
