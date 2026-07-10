"""Future payroll pre-review assistant boundary contracts."""

from enum import Enum

from pydantic import BaseModel, Field


class PayrollReviewCapability(str, Enum):
    READ_PREVIEW = "READ_PREVIEW"
    EXPLAIN_LINE_ITEMS = "EXPLAIN_LINE_ITEMS"
    FLAG_ANOMALIES = "FLAG_ANOMALIES"
    SUGGEST_HUMAN_REVIEW = "SUGGEST_HUMAN_REVIEW"


class PayrollReviewAssistantRequest(BaseModel):
    actor_user_id: int
    review_record_ids: list[int] = Field(default_factory=list)
    capability: PayrollReviewCapability


class PayrollReviewAssistantResult(BaseModel):
    summaries: list[dict[str, object]] = Field(default_factory=list)
    anomalies: list[dict[str, object]] = Field(default_factory=list)
    human_review_suggestions: list[str] = Field(default_factory=list)
    requires_hr_confirmation: bool = True
