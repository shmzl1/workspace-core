"""Seed data file checks for Sprint 1 demo data."""

import json
from pathlib import Path
from urllib.parse import urlsplit

SEED_DIR = Path(__file__).resolve().parents[3] / "data" / "seed"

REQUIRED_SEED_FILES = [
    "users.json",
    "employees.json",
    "jobs.json",
    "candidates.json",
    "interviewers.json",
    "meeting_rooms.json",
    "salary_records.json",
    "leave_balances.json",
    "attendance_records.json",
    "policy_documents.json",
]

OFFICIAL_POLICY_SOURCE_HOSTS = {
    "flk.npc.gov.cn",
    "xzfg.moj.gov.cn",
    "www.mohrss.gov.cn",
}


def test_required_seed_files_are_valid_json_arrays() -> None:
    for file_name in REQUIRED_SEED_FILES:
        path = SEED_DIR / file_name
        assert path.exists(), f"missing seed file: {file_name}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(payload, list), f"{file_name} must contain a JSON array"
        assert payload, f"{file_name} should not be empty"


def test_seed_files_use_demo_domains_not_real_credentials() -> None:
    combined = "\n".join((SEED_DIR / file_name).read_text(encoding="utf-8") for file_name in REQUIRED_SEED_FILES)

    assert "example.test" in combined
    assert "demo_only_not_for_login" in combined
    assert "sk-" not in combined.lower()
    assert "jwt" not in combined.lower()


def test_policy_seed_uses_active_official_public_sources() -> None:
    payload = json.loads((SEED_DIR / "policy_documents.json").read_text(encoding="utf-8"))
    document_codes = {item["document_code"] for item in payload}

    assert len(document_codes) == len(payload)
    for item in payload:
        source = urlsplit(item["source_path"])
        assert source.scheme == "https"
        assert source.hostname in OFFICIAL_POLICY_SOURCE_HOSTS
        assert item["is_active"] is True
        assert item["metadata_json"]["status"] == "现行有效"
        assert item["metadata_json"]["summary"].strip()
