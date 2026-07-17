"""CLI for the non-destructive candidate interview availability backfill."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from app.core.database import SessionLocal  # noqa: E402
from scripts.interview_availability_backfill import backfill_candidate_availability  # noqa: E402


def main() -> None:
    with SessionLocal.begin() as session:
        stats = backfill_candidate_availability(session)
    print(f"候选人总数：{stats.total_candidates}")
    print(f"已有有效时间：{stats.existing_valid_candidates}")
    print(f"新增候选人：{stats.backfilled_candidates}")
    print(f"新增候选人时间段：{stats.created_slots}")
    print(f"跳过候选人：{stats.skipped_candidates}")


if __name__ == "__main__":
    main()
