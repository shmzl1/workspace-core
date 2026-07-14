from datetime import datetime
from types import SimpleNamespace

from app.modules.policy import service as policy_service_module


class FakePolicyRepository:
    def __init__(self, documents: list[object]) -> None:
        self.documents = documents
        self.queries: list[str | None] = []

    def list_active(self, query: str | None = None):
        self.queries.append(query)
        return self.documents


def document(document_code: str, category: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        document_code=document_code,
        title=document_code,
        category=category,
        source_path=None,
        version="v1",
        metadata_json={},
        created_at=datetime(2026, 7, 1, 9, 0),
        updated_at=datetime(2026, 7, 2, 9, 0),
    )


def test_overview_groups_categories_in_stable_order(monkeypatch) -> None:
    repository = FakePolicyRepository([document("POL-2", "leave"), document("POL-1", "attendance"), document("POL-3", "leave")])
    monkeypatch.setattr(policy_service_module, "PolicyRepository", lambda _session: repository)

    overview = policy_service_module.PolicyService(object()).overview(query=" leave ")

    assert repository.queries == [" leave "]
    assert [item["category"] for item in overview["categories"]] == ["attendance", "leave"]
    assert [item["count"] for item in overview["categories"]] == [1, 2]
