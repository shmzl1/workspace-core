from datetime import date, datetime
from decimal import Decimal

from app.modules.payroll.services.pre_audit_service import PayrollPreAuditService


def test_json_ready_converts_nested_payroll_values_without_losing_structure() -> None:
    value = {
        "amount": Decimal("123.45"),
        "period": date(2026, 7, 1),
        "reviewed_at": datetime(2026, 7, 14, 9, 30),
        "items": [Decimal("50"), {"deduction": Decimal("3.5")}],
    }

    assert PayrollPreAuditService._json_ready(value) == {
        "amount": 123.45,
        "period": "2026-07-01",
        "reviewed_at": "2026-07-14T09:30:00",
        "items": [50.0, {"deduction": 3.5}],
    }
