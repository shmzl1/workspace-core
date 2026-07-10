"""Canonical structured schemas for planned recruitment intelligence work."""

from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    JobRequirementItem,
    JobRubric,
    ResumeEvidenceItem,
)
from app.modules.recruitment.intelligence.contracts import (
    ConfidenceBreakdown,
    EvidenceValidationResult,
    JobRubricDefinition,
    NormalizedSkill,
    ResumeExtractionResult,
)

__all__ = [
    "CandidateProfile",
    "ConfidenceBreakdown",
    "EvidenceValidationResult",
    "JobRequirementItem",
    "JobRubric",
    "JobRubricDefinition",
    "NormalizedSkill",
    "ResumeEvidenceItem",
    "ResumeExtractionResult",
]
