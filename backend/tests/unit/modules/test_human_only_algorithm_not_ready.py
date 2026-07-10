from unittest.mock import patch
from app.modules.payroll.services.access_service import PayrollAccessService


def test_payroll_access_returns_algorithm_not_ready_when_module_missing() -> None:
    service = PayrollAccessService()

    with patch("app.modules.payroll.services.access_service.load_human_only_function", return_value=None):
        result = service.check_salary_access({"requester": {"role": "HR_SPECIALIST"}, "records": []})

    assert result["status"] == "algorithm_not_ready"
    assert result["expected_module"] == "backend/app/human_only/salary_access_control.py"
    assert result["expected_function"] == "check_salary_access"
