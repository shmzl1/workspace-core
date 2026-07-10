"""Validate and detach database-backed context before an Agent run starts."""

from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentJobContext,
    RecruitmentRunContext,
    RecruitmentRunRequest,
)
from app.core.exceptions import TalentFlowError
from app.modules.recruitment.service import RecruitmentService


class RecruitmentRunContextService:
    def __init__(self, recruitment_service: RecruitmentService) -> None:
        self.recruitment_service = recruitment_service

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
        return RecruitmentRunContext(
            request=normalized_request,
            job=RecruitmentJobContext(
                job_id=job.id,
                job_code=job.job_code,
                job_title=job.title,
                department=job.department,
                status=job.status,
            ),
            candidate_ids=candidate_ids,
            application_ids=[application_by_candidate[candidate_id] for candidate_id in candidate_ids],
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

