from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: int
    actor_user_id: int | None = None
    actor_role: str
    target_employee_id: int | None = None
    action: str
    resource_type: str
    resource_id: int | None = None
    requested_fields: list[str]
    result: str
    reason: str | None = None
    trace_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
