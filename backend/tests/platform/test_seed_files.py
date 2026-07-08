"""Seed data file checks for Sprint 1 demo data."""

import json
from pathlib import Path

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
]


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
