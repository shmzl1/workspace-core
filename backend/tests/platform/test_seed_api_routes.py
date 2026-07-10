"""Unified API route checks for front-end seed data access."""

from fastapi.testclient import TestClient

from app.api.v1.endpoints.recruitment import get_recruitment_service
from app.main import app
from app.core.dependencies import get_current_user
from app.modules.auth.models import User


class FakeRecruitmentService:
    def list_jobs(self) -> list[dict]:
        return [
            {
                "id": 1,
                "job_code": "JOB-JAVA-INTERN-001",
                "title": "Java 后端开发实习生",
                "status": "OPEN",
            }
        ]


def test_frontend_can_read_seed_like_jobs_through_unified_api() -> None:
    mock_user = User(id=3, username="linyuqing", role="HR_SPECIALIST", permissions=["recruitment.read"])
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_recruitment_service] = lambda: FakeRecruitmentService()
    try:
        response = TestClient(app).get(
            "/api/v1/recruitment/jobs",
            headers={"X-Trace-Id": "pytest-trace-seed-api"},
        )
    finally:
        app.dependency_overrides.clear()

    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["error"] is None
    assert body["trace_id"] == "pytest-trace-seed-api"
    assert body["data"][0]["job_code"] == "JOB-JAVA-INTERN-001"
