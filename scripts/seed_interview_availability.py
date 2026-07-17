"""Compatibility CLI for the complete non-destructive interview backfill."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from scripts.interview_availability_backfill import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
