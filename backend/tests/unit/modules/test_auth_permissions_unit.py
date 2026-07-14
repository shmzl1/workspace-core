import pytest

from app.modules.auth.permissions import ROLE_DEFAULT_PERMISSIONS, normalize_permissions


@pytest.mark.parametrize("value", [None, "employee.self.read", 123, {"permission": True}, object()])
def test_normalize_permissions_rejects_non_collections(value: object) -> None:
    assert normalize_permissions(value) == []


def test_normalize_permissions_trims_deduplicates_filters_and_sorts() -> None:
    raw = [
        " policy.read ",
        "",
        "policy.read",
        "agent.hr.use",
        "   ",
        None,
        7,
    ]
    assert normalize_permissions(raw) == ["agent.hr.use", "policy.read"]


def test_normalize_permissions_accepts_tuple_and_set() -> None:
    assert normalize_permissions(("b", "a", "b")) == ["a", "b"]
    assert normalize_permissions({"z", "a"}) == ["a", "z"]


def test_role_defaults_are_unique_and_non_blank() -> None:
    for permissions in ROLE_DEFAULT_PERMISSIONS.values():
        assert permissions
        assert len(permissions) == len(set(permissions))
        assert all(item == item.strip() and item for item in permissions)
