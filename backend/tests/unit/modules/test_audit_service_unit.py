from datetime import datetime, timezone
from types import SimpleNamespace

from app.modules.audit.service import AuditService


class FakeAuditRepository:
    def __init__(self, logs: list[object]) -> None:
        self.logs = logs
        self.requested_limits: list[int] = []

    def list_logs(self, limit: int):
        self.requested_limits.append(limit)
        return self.logs


def test_list_logs_serializes_auditable_fields_and_forwards_limit() -> None:
    log = SimpleNamespace(
        id=1,
        actor_user_id=7,
        actor_role="HR_SPECIALIST",
        target_employee_id=8,
        action="READ_EMPLOYEE",
        resource_type="EMPLOYEE",
        resource_id=8,
        requested_fields=["full_name"],
        result="SUCCESS",
        reason=None,
        trace_id="trace-audit",
        created_at=datetime(2026, 7, 14, 9, 0, tzinfo=timezone.utc),
    )
    repository = FakeAuditRepository([log])

    result = AuditService(repository).list_logs(limit=25)

    assert repository.requested_limits == [25]
    assert result == [{
        "id": 1,
        "actor_user_id": 7,
        "actor_role": "HR_SPECIALIST",
        "target_employee_id": 8,
        "action": "READ_EMPLOYEE",
        "resource_type": "EMPLOYEE",
        "resource_id": 8,
        "requested_fields": ["full_name"],
        "result": "SUCCESS",
        "reason": None,
        "trace_id": "trace-audit",
        "created_at": "2026-07-14T09:00:00+00:00",
    }]
