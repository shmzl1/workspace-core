"""Protocol for the planned resume fact-extraction boundary."""

from typing import Mapping, Protocol

from app.modules.recruitment.intelligence.schemas import ResumeExtractionResult


class ResumeExtractor(Protocol):
    def extract(
        self,
        candidate_id: int,
        structured_resume: Mapping[str, object],
    ) -> ResumeExtractionResult: ...
