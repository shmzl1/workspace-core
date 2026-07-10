"""Event publication interface implemented by the Sprint 2.1 runtime store."""

from collections.abc import AsyncIterator, Sequence
from typing import Protocol

from app.agents.shared.contracts import AgentEvent


class AgentEventPublisher(Protocol):
    async def publish(self, event: AgentEvent) -> None: ...

    async def history(self, run_id: str) -> Sequence[AgentEvent]: ...

    def subscribe(self, run_id: str) -> AsyncIterator[AgentEvent]: ...

