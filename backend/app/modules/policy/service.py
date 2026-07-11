"""Policy document service."""

from sqlalchemy.orm import Session

from app.modules._serialization import model_to_dict
from app.modules.policy.repository import PolicyRepository


class PolicyService:
    def __init__(self, session: Session) -> None:
        self.repository = PolicyRepository(session)

    def list_documents(self, query: str | None = None) -> list[dict]:
        return [model_to_dict(document, ["id", "document_code", "title", "category", "source_path", "version", "metadata_json", "created_at", "updated_at"]) for document in self.repository.list_active(query)]

    def overview(self, query: str | None = None) -> dict:
        documents = self.list_documents(query)
        categories: dict[str, int] = {}
        for document in documents:
            categories[document["category"]] = categories.get(document["category"], 0) + 1
        return {"documents": documents, "categories": [{"category": name, "count": count} for name, count in sorted(categories.items())]}
