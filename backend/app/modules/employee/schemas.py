from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class EmployeeBase(BaseModel):
    employee_no: str
    full_name: str
    department: str
    job_title: str
    email: str | None = None
    phone: str | None = None
    hire_date: date | None = None
    employment_status: str


class EmployeeRead(EmployeeBase):
    id: int
    user_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class LeaveBalanceRead(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    year: int
    total_days: Decimal
    used_days: Decimal

    model_config = ConfigDict(from_attributes=True)


class EmployeeProfileResponse(BaseModel):
    employee: EmployeeRead
    leave_balance: LeaveBalanceRead | None = None
