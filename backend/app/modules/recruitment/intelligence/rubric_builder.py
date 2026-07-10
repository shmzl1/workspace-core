"""Protocol for planned job-rubric construction."""

from collections.abc import Sequence
from typing import Mapping, Protocol

from app.modules.recruitment.intelligence.schemas import JobRubricDefinition


class RubricBuilder(Protocol):
    def build(
        self,
        job_id: int,
        requirements: Sequence[Mapping[str, object]],
    ) -> JobRubricDefinition: ...
