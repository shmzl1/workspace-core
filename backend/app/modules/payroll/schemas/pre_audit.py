"""Payroll review schemas for Sprint 1 HR display."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class PayrollLineItemRead(BaseModel):
    id: int
    item_type: str
    item_name: str
    amount: Decimal
    source_type: str | None = None
    source_reference_json: dict[str, Any] = Field(default_factory=dict)
    calculation_detail_json: dict[str, Any] = Field(default_factory=dict)


class PayrollReviewRecordRead(BaseModel):
    id: int
    employee_id: int
    employee_name: str | None = None
    payroll_period_id: int
    period_code: str | None = None
    status: str
    base_salary_snapshot: Decimal
    standard_work_days_snapshot: Decimal
    total_earnings: Decimal
    total_deductions: Decimal
    net_salary_preview: Decimal
    calculation_snapshot: dict[str, Any] = Field(default_factory=dict)
    confirmed_at: datetime | None = None
    permission_status: str = "权限审计待联调"
    line_items: list[PayrollLineItemRead] = Field(default_factory=list)


class PayrollReviewListRead(BaseModel):
    records: list[PayrollReviewRecordRead]
    status_note: str
