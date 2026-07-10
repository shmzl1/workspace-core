"""Protocol for planned skill normalization; no normalization algorithm is implemented."""

from collections.abc import Sequence
from typing import Protocol

from app.modules.recruitment.intelligence.schemas import NormalizedSkill


class SkillNormalizer(Protocol):
    def normalize(self, raw_skills: Sequence[str]) -> Sequence[NormalizedSkill]: ...
