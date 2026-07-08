"""Security helper placeholders.

Authorization decisions are server-side responsibilities. This module must not
store real secrets.
"""

from dataclasses import dataclass

from app.core.exceptions import TalentFlowError


@dataclass(frozen=True)
class DemoIdentity:
    user_id: int
    username: str
    role: str
    employee_id: int | None = None


def mask_sensitive(value: str | None, visible_tail: int = 4) -> str | None:
    if value is None:
        return None
    if len(value) <= visible_tail:
        return "*" * len(value)
    return "*" * (len(value) - visible_tail) + value[-visible_tail:]


def parse_demo_identity(raw: str | None) -> DemoIdentity:
    """Parse demo identity from a header value.

    Expected format: ``user_id:username:role[:employee_id]``.
    """

    if not raw:
        return DemoIdentity(user_id=1, username="hr_demo", role="HR_SPECIALIST", employee_id=1)
    parts = [item.strip() for item in raw.split(":")]
    if len(parts) not in (3, 4):
        raise TalentFlowError("INVALID_DEMO_IDENTITY", "演示身份格式应为 user_id:username:role[:employee_id]", 401)
    try:
        user_id = int(parts[0])
        employee_id = int(parts[3]) if len(parts) == 4 and parts[3] else None
    except ValueError as exc:
        raise TalentFlowError("INVALID_DEMO_IDENTITY", "演示身份中的用户或员工编号必须为整数", 401) from exc
    return DemoIdentity(user_id=user_id, username=parts[1], role=parts[2], employee_id=employee_id)
