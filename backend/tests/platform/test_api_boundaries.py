"""Static boundary checks for Sprint 1 API layering."""

from pathlib import Path

ENDPOINT_DIR = Path(__file__).resolve().parents[2] / "app" / "api" / "v1" / "endpoints"


def endpoint_sources() -> list[tuple[Path, str]]:
    return [(path, path.read_text(encoding="utf-8")) for path in ENDPOINT_DIR.glob("*.py")]


def test_routes_do_not_import_or_call_human_only() -> None:
    for path, source in endpoint_sources():
        assert "human_only" not in source, f"{path.name} must not touch AI forbidden zone"


def test_routes_do_not_run_database_queries_directly() -> None:
    forbidden_tokens = ("select(", "insert(", "update(", "delete(", "SessionLocal")
    for path, source in endpoint_sources():
        for token in forbidden_tokens:
            assert token not in source, f"{path.name} contains direct database token {token}"


def test_routes_do_not_import_repositories_directly() -> None:
    for path, source in endpoint_sources():
        assert ".repository import" not in source, f"{path.name} imports Repository directly"
        assert "Repository(" not in source, f"{path.name} constructs Repository directly"
