"""Protocol for planned deterministic confidence calculation."""

from typing import Mapping, Protocol

from app.modules.recruitment.intelligence.schemas import ConfidenceBreakdown


class ConfidenceCalculator(Protocol):
    def calculate(self, factors: Mapping[str, float]) -> ConfidenceBreakdown: ...
