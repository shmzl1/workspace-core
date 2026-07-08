from datetime import date
from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity
from app.modules._serialization import model_to_dict
from app.modules.payroll.models import SalaryRecord
from app.modules.payroll.repository import PayrollRepository
from app.modules.payroll.services.access_service import PayrollAccessService


class EmployeeSalaryService:
    def __init__(self, repository_or_session, access_service: PayrollAccessService = None) -> None:
        if isinstance(repository_or_session, Session):
            self.db = repository_or_session
            self.repository = PayrollRepository(repository_or_session)
            self.access_service = access_service or PayrollAccessService(repository_or_session)
        else:
            self.repository = repository_or_session
            self.access_service = access_service
            self.db = repository_or_session.session

    @classmethod
    def from_session(cls, session: Session) -> "EmployeeSalaryService":
        return cls(PayrollRepository(session), PayrollAccessService(session))

    def get_employee_salary(
        self,
        actor_user_id: int,
        actor_role: str,
        actor_employee_id: int | None,
        target_employee_id: int,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> dict:
        """
        Retrieve salary info for an employee, verifying access and applying field-level masking.
        """
        # 1. Verify access and get accessible fields list
        accessible_fields = self.access_service.verify_and_log_access(
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            actor_employee_id=actor_employee_id,
            target_employee_id=target_employee_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # 2. Query the active salary record
        today = date.today()
        record = self.db.query(SalaryRecord).filter(
            SalaryRecord.employee_id == target_employee_id,
            SalaryRecord.effective_from <= today
        ).filter(
            (SalaryRecord.effective_to == None) | (SalaryRecord.effective_to >= today)
        ).order_by(SalaryRecord.effective_from.desc()).first()

        # If no active salary record found, fall back to any salary record
        if not record:
            record = self.db.query(SalaryRecord).filter(
                SalaryRecord.employee_id == target_employee_id
            ).order_by(SalaryRecord.effective_from.desc()).first()

        if not record:
            raise TalentFlowError("SALARY_RECORD_NOT_FOUND", "未找到该员工的薪资记录")

        # 3. Apply masking based on accessible fields
        data = {}
        data["id"] = record.id
        data["employee_id"] = record.employee_id
        
        # Mask each field if not allowed
        data["base_salary"] = record.base_salary if "base_salary" in accessible_fields else None
        data["currency"] = record.currency if "currency" in accessible_fields else None
        data["effective_from"] = record.effective_from if "effective_from" in accessible_fields else None
        data["effective_to"] = record.effective_to if "effective_to" in accessible_fields else None

        return data

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
