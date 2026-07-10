"""Validate and detach database-backed context before an Agent run starts."""

from datetime import date
from typing import Protocol

from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentCandidateContext,
    RecruitmentJobContext,
    RecruitmentRunContext,
    RecruitmentRunRequest,
)
from app.core.exceptions import TalentFlowError
from app.modules.recruitment.service import RecruitmentService


class InterviewLookupService(Protocol):
    def application_ids_with_interviews(self, application_ids: list[int]) -> set[int]: ...


class RecruitmentRunContextService:
    def __init__(
        self,
        recruitment_service: RecruitmentService,
        interview_service: InterviewLookupService | None = None,
    ) -> None:
        self.recruitment_service = recruitment_service
        self.interview_service = interview_service

    def validate(self, request: RecruitmentRunRequest) -> RecruitmentRunContext:
        candidate_ids = self._deduplicate(request.candidate_ids)
        if not candidate_ids:
            raise TalentFlowError(
                "AGENT_CANDIDATES_REQUIRED",
                "至少需要选择一名候选人。",
                400,
            )

        job = self.recruitment_service.get_job(request.goal.job_id)
        rows = self.recruitment_service.list_applications_for_job(job.id)
        application_by_candidate = {
            int(row["candidate"]["id"]): int(row["application"]["id"])
            for row in rows
        }
        missing = [candidate_id for candidate_id in candidate_ids if candidate_id not in application_by_candidate]
        if missing:
            raise TalentFlowError(
                "CANDIDATE_NOT_IN_JOB",
                "所选候选人不存在或未投递当前岗位。",
                400,
            )

        normalized_goal = request.goal.model_copy(
            update={"job_title": job.title, "department": job.department}
        )
        normalized_request = RecruitmentRunRequest(
            goal=normalized_goal,
            candidate_ids=candidate_ids,
        )
        candidate_rows = self.recruitment_service.list_agent_candidate_inputs_for_job(job.id, candidate_ids)
        candidate_by_id = {
            int(row["candidate_id"]): RecruitmentCandidateContext.model_validate(row)
            for row in candidate_rows
        }
        candidates = [candidate_by_id[candidate_id] for candidate_id in candidate_ids if candidate_id in candidate_by_id]
        context_candidate_ids = set(candidate_by_id)
        missing_context = [candidate_id for candidate_id in candidate_ids if candidate_id not in context_candidate_ids]
        if missing_context:
            raise TalentFlowError("CANDIDATE_CONTEXT_NOT_FOUND", "候选人解析上下文读取失败。", 500)
        application_ids = [application_by_candidate[candidate_id] for candidate_id in candidate_ids]
        interviewed_applications = (
            self.interview_service.application_ids_with_interviews(application_ids)
            if self.interview_service is not None
            else set()
        )
        interviewed_candidates = [
            candidate_id
            for candidate_id in candidate_ids
            if application_by_candidate[candidate_id] in interviewed_applications
        ]
        effective_at = job.created_at or job.updated_at
        effective_date = effective_at.date() if effective_at is not None else date.today()
        version_at = job.updated_at or job.created_at
        source_version = f"job-{version_at.strftime('%Y%m%d%H%M%S')}" if version_at else "job-record-v1"
        return RecruitmentRunContext(
            request=normalized_request,
            job=RecruitmentJobContext(
                job_id=job.id,
                job_code=job.job_code,
                job_title=job.title,
                department=job.department,
                status=job.status,
                description=job.description,
                required_skills=[str(item) for item in job.required_skills],
                preferred_skills=[str(item) for item in job.preferred_skills],
                min_experience_months=job.min_experience_months,
                source_version=source_version,
                effective_date=effective_date,
            ),
            candidate_ids=candidate_ids,
            application_ids=application_ids,
            candidates=candidates,
            interview_candidate_ids=interviewed_candidates,
        )

    @staticmethod
    def _deduplicate(candidate_ids: list[int]) -> list[int]:
        seen: set[int] = set()
        result: list[int] = []
        for candidate_id in candidate_ids:
            if candidate_id not in seen:
                seen.add(candidate_id)
                result.append(candidate_id)
        return result

