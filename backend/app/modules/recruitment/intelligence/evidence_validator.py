"""Protocol for planned evidence validation."""

from typing import Mapping, Protocol

from app.modules.recruitment.intelligence.schemas import EvidenceValidationResult


class EvidenceValidator(Protocol):
    def validate(
        self,
        evidence_id: str,
        evidence: Mapping[str, object],
    ) -> EvidenceValidationResult: ...
