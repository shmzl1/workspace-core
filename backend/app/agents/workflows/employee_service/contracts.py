"""Future employee-service Agent boundary contracts."""

from enum import Enum

from pydantic import BaseModel, Field

from app.agents.shared.contracts import KnowledgeSourceReference


class EmployeeServiceCapability(str, Enum):
    TODAY_ATTENDANCE = "TODAY_ATTENDANCE"
    MONTHLY_ATTENDANCE = "MONTHLY_ATTENDANCE"
    ANNUAL_LEAVE = "ANNUAL_LEAVE"
    SALARY_SUMMARY = "SALARY_SUMMARY"
    POLICY_QUERY = "POLICY_QUERY"


class EmployeeServiceRequest(BaseModel):
    actor_user_id: int
    employee_id: int
    capability: EmployeeServiceCapability
    query: str | None = None


class EmployeeServiceResult(BaseModel):
    employee_id: int
    capability: EmployeeServiceCapability
    summary: dict[str, object] = Field(default_factory=dict)
    sources: list[KnowledgeSourceReference] = Field(default_factory=list)
