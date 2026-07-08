from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class SalaryRead(BaseModel):
    id: int
    employee_id: int
    base_salary: Decimal | None = None
    currency: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
