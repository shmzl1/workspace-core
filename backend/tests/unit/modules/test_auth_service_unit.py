from types import SimpleNamespace

import pytest

from app.core.exceptions import TalentFlowError
from app.modules.auth.service import AuthService


class FakeAuthRepository:
    def __init__(self, employee=None) -> None:
        self.employee = employee

    def get_employee_for_user(self, user_id: int):
        return self.employee


def user(*, is_active: bool = True, permissions=None) -> SimpleNamespace:
    return SimpleNamespace(
        id=7,
        username="ada",
        role="HR_SPECIALIST",
        is_active=is_active,
        permissions=permissions,
    )


def test_user_read_normalizes_permissions_and_maps_employee_profile() -> None:
    employee = SimpleNamespace(id=17, full_name="Ada Lovelace", department="Engineering", job_title="Engineer")
    result = AuthService(FakeAuthRepository(employee)).user_read(
        user(permissions=[" policy.read ", "policy.read", 3, ""])
    )

    assert result.permissions == ["policy.read"]
    assert result.employee_id == 17
    assert result.full_name == "Ada Lovelace"


def test_get_current_user_rejects_inactive_account() -> None:
    with pytest.raises(TalentFlowError) as error:
        AuthService(FakeAuthRepository()).get_current_user(user(is_active=False))

    assert error.value.code == "USER_INACTIVE"
