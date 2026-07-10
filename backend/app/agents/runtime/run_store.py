"""Bounded in-process storage for Sprint 2.1 Agent runs."""

import asyncio
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.agents.shared import AgentEvent, AgentEventType
from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentDecisionState,
    RecruitmentRunSnapshot,
)
from app.core.exceptions import TalentFlowError

TERMINAL_EVENT_TYPES = {AgentEventType.WORKFLOW_COMPLETED, AgentEventType.WORKFLOW_FAILED}


@dataclass
class RecruitmentRunRecord:
    run_id: str
    owner_user_id: int
    state: RecruitmentDecisionState
    snapshot: RecruitmentRunSnapshot
    events: list[AgentEvent] = field(default_factory=list)
    subscribers: list[asyncio.Queue[AgentEvent | None]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    terminal: bool = False


class InMemoryAgentRunStore:
    def __init__(
        self,
        max_runs: int = 100,
        max_events_per_run: int = 500,
        terminal_ttl: timedelta = timedelta(hours=2),
    ) -> None:
        self.max_runs = max_runs
        self.max_events_per_run = max_events_per_run
        self.terminal_ttl = terminal_ttl
        self._runs: OrderedDict[str, RecruitmentRunRecord] = OrderedDict()
        self._lock = asyncio.Lock()

    async def create(
        self,
        owner_user_id: int,
        state: RecruitmentDecisionState,
        snapshot: RecruitmentRunSnapshot,
    ) -> RecruitmentRunRecord:
        now = datetime.now(timezone.utc)
        async with self._lock:
            self._cleanup_expired_locked(now)
            if len(self._runs) >= self.max_runs:
                removable = next((key for key, value in self._runs.items() if value.terminal), None)
                if removable is None:
                    raise TalentFlowError(
                        "AGENT_RUN_CAPACITY_REACHED",
                        "当前策略运行数量已达上限，请稍后重试。",
                        503,
                    )
                self._runs.pop(removable)
            record = RecruitmentRunRecord(
                run_id=snapshot.run_id,
                owner_user_id=owner_user_id,
                state=state.model_copy(deep=True),
                snapshot=snapshot.model_copy(deep=True),
                created_at=now,
                updated_at=now,
            )
            self._runs[record.run_id] = record
            return self._copy_record(record)

    async def get(self, run_id: str) -> RecruitmentRunRecord:
        async with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                raise self._not_found()
            return self._copy_record(record)

    async def get_owned(self, run_id: str, owner_user_id: int) -> RecruitmentRunRecord:
        async with self._lock:
            record = self._runs.get(run_id)
            if record is None or record.owner_user_id != owner_user_id:
                raise self._not_found()
            return self._copy_record(record)

    async def update_snapshot(
        self,
        run_id: str,
        snapshot: RecruitmentRunSnapshot,
        state: RecruitmentDecisionState | None = None,
        terminal: bool | None = None,
    ) -> RecruitmentRunRecord:
        now = datetime.now(timezone.utc)
        async with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                raise self._not_found()
            stored_snapshot = snapshot.model_copy(deep=True)
            stored_snapshot.events = [event.model_copy(deep=True) for event in record.events]
            stored_snapshot.updated_at = now
            record.snapshot = stored_snapshot
            if state is not None:
                stored_state = state.model_copy(deep=True)
                stored_state.events = [event.model_copy(deep=True) for event in record.events]
                record.state = stored_state
            if terminal is not None:
                record.terminal = terminal
            record.updated_at = now
            return self._copy_record(record)

    async def append_event(self, run_id: str, event: AgentEvent) -> None:
        now = datetime.now(timezone.utc)
        async with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                raise self._not_found()
            record.events.append(event.model_copy(deep=True))
            if len(record.events) > self.max_events_per_run:
                record.events = record.events[-self.max_events_per_run :]
            record.snapshot.events = [item.model_copy(deep=True) for item in record.events]
            record.snapshot.updated_at = now
            record.state.events = [item.model_copy(deep=True) for item in record.events]
            record.updated_at = now
            is_terminal_event = event.event_type in TERMINAL_EVENT_TYPES
            if is_terminal_event:
                record.terminal = True
            for queue in tuple(record.subscribers):
                self._put_bounded(queue, event.model_copy(deep=True))
                if is_terminal_event:
                    self._put_bounded(queue, None)

    async def history(self, run_id: str) -> list[AgentEvent]:
        async with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                raise self._not_found()
            return [event.model_copy(deep=True) for event in record.events]

    async def subscribe(self, run_id: str) -> asyncio.Queue[AgentEvent | None]:
        queue: asyncio.Queue[AgentEvent | None] = asyncio.Queue(maxsize=self.max_events_per_run)
        async with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                raise self._not_found()
            record.subscribers.append(queue)
            return queue

    async def unsubscribe(self, run_id: str, queue: asyncio.Queue[AgentEvent | None]) -> None:
        async with self._lock:
            record = self._runs.get(run_id)
            if record is not None and queue in record.subscribers:
                record.subscribers.remove(queue)

    async def cleanup_expired(self) -> int:
        async with self._lock:
            return self._cleanup_expired_locked(datetime.now(timezone.utc))

    def _cleanup_expired_locked(self, now: datetime) -> int:
        expired = [
            run_id
            for run_id, record in self._runs.items()
            if record.terminal and now - record.updated_at > self.terminal_ttl
        ]
        for run_id in expired:
            self._runs.pop(run_id, None)
        return len(expired)

    @staticmethod
    def _put_bounded(queue: asyncio.Queue[AgentEvent | None], item: AgentEvent | None) -> None:
        if queue.full():
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                return
        queue.put_nowait(item)

    @staticmethod
    def _copy_record(record: RecruitmentRunRecord) -> RecruitmentRunRecord:
        return RecruitmentRunRecord(
            run_id=record.run_id,
            owner_user_id=record.owner_user_id,
            state=record.state.model_copy(deep=True),
            snapshot=record.snapshot.model_copy(deep=True),
            events=[event.model_copy(deep=True) for event in record.events],
            subscribers=[],
            created_at=record.created_at,
            updated_at=record.updated_at,
            terminal=record.terminal,
        )

    @staticmethod
    def _not_found() -> TalentFlowError:
        return TalentFlowError("AGENT_RUN_NOT_FOUND", "Agent Run 不存在或不可访问。", 404)


agent_run_store = InMemoryAgentRunStore()
