"""Employee salary query service boundary."""

from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity
from app.modules._serialization import model_to_dict
from app.modules.payroll.repository import PayrollRepository
from app.modules.payroll.services.access_service import PayrollAccessService
from sqlalchemy.orm import Session


class EmployeeSalaryService:
    def __init__(self, repository: PayrollRepository, access_service: PayrollAccessService) -> None:
        self.repository = repository
        self.access_service = access_service

    @classmethod
    def from_session(cls, session: Session) -> "EmployeeSalaryService":
        return cls(PayrollRepository(session), PayrollAccessService())

    def get_salary_summary(self, identity: DemoIdentity, target_employee_id: int) -> dict:
        requested_fields = ["base_salary", "currency", "effective_from", "effective_to"]
        decision = self.access_service.check_salary_access(identity, target_employee_id, requested_fields)
        if not decision.allowed:
            raise TalentFlowError("SALARY_ACCESS_DENIED", decision.reason or "无权访问该员工薪资", 403)
        record = self.repository.get_latest_salary(target_employee_id)
        if record is None:
            raise TalentFlowError("SALARY_RECORD_NOT_FOUND", "薪资记录不存在", 404)
        data = model_to_dict(record, ["id", "employee_id", "base_salary", "currency", "effective_from", "effective_to"])
        return {key: value for key, value in data.items() if key in {"id", "employee_id", *decision.fields}}
