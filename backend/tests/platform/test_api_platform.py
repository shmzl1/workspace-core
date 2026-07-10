"""Sprint 1 FastAPI platform acceptance tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_unified_response_with_trace_id() -> None:
    response = client.get("/health", headers={"X-Trace-Id": "pytest-trace-health"})

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"status": "ok"},
        "error": None,
        "trace_id": "pytest-trace-health",
    }


def test_openapi_contains_sprint1_route_groups() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]

    assert "/api/v1/recruitment/jobs" in paths
    assert "/api/v1/recruitment/candidates" in paths
    assert "/api/v1/attendance/today" in paths
    assert "/api/v1/payroll/me" in paths
    assert "/api/v1/audit/logs" in paths



def test_unknown_path_returns_unified_error() -> None:
    response = client.get("/api/v1/not-found", headers={"X-Trace-Id": "pytest-trace-404"})

    body = response.json()
    assert response.status_code == 404
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "HTTP_ERROR"
    assert body["trace_id"] == "pytest-trace-404"
