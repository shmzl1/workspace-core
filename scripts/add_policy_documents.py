"""Idempotently add the built-in policy-center documents to PostgreSQL.

This script intentionally does not reset any business data.  It is safe to
run repeatedly: records are matched by ``document_code`` and updated in place.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from sqlalchemy import select  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.modules.policy.models import PolicyDocument  # noqa: E402


DOCUMENTS = [
    {
        "document_code": "TF-POL-005",
        "title": "混合办公与远程协作规范",
        "category": "办公协作",
        "source_path": "docs/policies/hybrid-work.pdf",
        "version": "v1.0",
        "metadata_json": {"summary": "适用于经主管批准的混合办公安排，明确办公地点、信息安全和工作时段要求。"},
    },
    {
        "document_code": "TF-POL-006",
        "title": "员工健康体检与心理支持服务说明",
        "category": "员工福利",
        "source_path": "docs/policies/wellbeing-support.pdf",
        "version": "v1.2",
        "metadata_json": {"summary": "说明年度健康体检、员工援助计划及预约方式，不保存或展示个人健康信息。"},
    },
]


def main() -> None:
    with SessionLocal() as session:
        for payload in DOCUMENTS:
            document = session.scalar(select(PolicyDocument).where(PolicyDocument.document_code == payload["document_code"]))
            if document is None:
                session.add(PolicyDocument(**payload))
            else:
                for field, value in payload.items():
                    setattr(document, field, value)
        session.commit()
    print(f"Policy documents upserted: {len(DOCUMENTS)}")


if __name__ == "__main__":
    main()
