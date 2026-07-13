"""PostgreSQL-backed Agent Run Store with in-process SSE subscriber queues."""

import asyncio
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.agents.runtime.run_store import RecruitmentRunRecord
from app.agents.shared import (
    AgentErrorInfo,
    AgentEvent,
    AgentEventType,
    AgentNodeStatus,
    AgentRunStatus,
)
from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentDecisionState,
    RecruitmentRunSnapshot,
)
from app.core.exceptions import TalentFlowError
from app.modules.agent_runtime.models import (
    AgentEventRecord,
    AgentRun,
    AgentRunNode,
    AgentToolCall,
)
from app.modules.agent_runtime.repository import AgentRunRepository


TERMINAL_RUN_STATUSES = {
    AgentRunStatus.COMPLETED,
    AgentRunStatus.FAILED,
    AgentRunStatus.CANCELLED,
}
TERMINAL_EVENT_TYPES = {
    AgentEventType.WORKFLOW_COMPLETED,
    AgentEventType.WORKFLOW_FAILED,
}
NODE_COMPLETION_EVENTS = {
    AgentEventType.AGENT_COMPLETED,
    AgentEventType.REVIEW_COMPLETED,
    AgentEventType.REPORT_GENERATED,
}
SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "contact",
    "database_url",
    "jwt",
    "password",
    "phone",
    "resume",
    "salary",
    "token",
}


class PostgreSQLAgentRunStore:
    """Persist Run data in PostgreSQL while keeping only live SSE queues in memory."""

    mode = "POSTGRESQL"

    def __init__(self, session_factory: Callable[[], Session], queue_size: int = 500) -> None:
        self._session_factory = session_factory
        self._queue_size = queue_size
        self._subscribers: dict[str, list[asyncio.Queue[AgentEvent | None]]] = {}
        self._run_locks: dict[str, asyncio.Lock] = {}

    async def create(
        self,
        owner_user_id: int,
        state: RecruitmentDecisionState,
        snapshot: RecruitmentRunSnapshot,
    ) -> RecruitmentRunRecord:
        now = datetime.now(timezone.utc)
        try:
            with self._session_factory() as session, session.begin():
                repository = AgentRunRepository(session)
                repository.add_run(AgentRun(
                    run_id=snapshot.run_id,
                    workflow_type="RECRUITMENT_DECISION",
                    owner_user_id=owner_user_id,
                    trace_id=snapshot.trace_id,
                    status=snapshot.status.value,
                    current_agent=snapshot.current_agent,
                    current_node=snapshot.current_node,
                    current_candidate_id=snapshot.current_candidate_id,
                    terminal=False,
                    state_json=_persistence_json(state.model_dump(mode="json", exclude={"events"})),
                    snapshot_json=_persistence_json(snapshot.model_dump(mode="json", exclude={"events"})),
                    error_json=None,
                    created_at=now,
                    updated_at=now,
                ))
                for node_name, status in snapshot.nodes.items():
                    repository.add_node(AgentRunNode(
                        run_id=snapshot.run_id,
                        node_name=node_name,
                        status=status.value,
                        attempt=1,
                    ))
        except IntegrityError as exc:
            raise TalentFlowError("AGENT_RUN_ALREADY_EXISTS", "Agent Run 已存在。", 409) from exc
        return await self.get(snapshot.run_id)

    async def get(self, run_id: str) -> RecruitmentRunRecord:
        with self._session_factory() as session:
            repository = AgentRunRepository(session)
            run = repository.get_run(run_id)
            if run is None:
                raise self._not_found()
            return self._record(run, repository.list_events(run_id))

    async def get_owned(self, run_id: str, owner_user_id: int) -> RecruitmentRunRecord:
        with self._session_factory() as session:
            repository = AgentRunRepository(session)
            run = repository.get_owned(run_id, owner_user_id)
            if run is None:
                raise self._not_found()
            return self._record(run, repository.list_events(run_id))

    async def update_snapshot(
        self,
        run_id: str,
        snapshot: RecruitmentRunSnapshot,
        state: RecruitmentDecisionState | None = None,
        terminal: bool | None = None,
    ) -> RecruitmentRunRecord:
        now = datetime.now(timezone.utc)
        async with self._lock_for(run_id):
            with self._session_factory() as session, session.begin():
                repository = AgentRunRepository(session)
                run = repository.get_run(run_id, for_update=True)
                if run is None:
                    raise self._not_found()
                run.status = snapshot.status.value
                run.current_agent = snapshot.current_agent
                run.current_node = snapshot.current_node
                run.current_candidate_id = snapshot.current_candidate_id
                run.snapshot_json = _persistence_json(snapshot.model_dump(mode="json", exclude={"events"}))
                if state is not None:
                    run.state_json = _persistence_json(state.model_dump(mode="json", exclude={"events"}))
                run.error_json = snapshot.error.model_dump(mode="json") if snapshot.error else None
                inferred_terminal = snapshot.status in TERMINAL_RUN_STATUSES
                run.terminal = inferred_terminal if terminal is None else terminal
                if snapshot.status is AgentRunStatus.RUNNING and run.started_at is None:
                    run.started_at = now
                if run.terminal and run.completed_at is None:
                    run.completed_at = now
                run.updated_at = now
                self._sync_nodes(repository, run_id, snapshot, now)
            return await self.get(run_id)

    async def append_event(self, run_id: str, event: AgentEvent) -> None:
        async with self._lock_for(run_id):
            with self._session_factory() as session, session.begin():
                repository = AgentRunRepository(session)
                run = repository.get_run(run_id, for_update=True)
                if run is None:
                    raise self._not_found()
                sequence_no = repository.next_sequence(run_id)
                repository.add_event(self._event_record(event, sequence_no))
                self._sync_node_from_event(repository, event)
                self._sync_tool_call(repository, event)
                run.updated_at = event.created_at
                if event.event_type in TERMINAL_EVENT_TYPES:
                    run.terminal = True
                    run.completed_at = run.completed_at or event.created_at
            self._notify(run_id, event)

    async def history(self, run_id: str) -> list[AgentEvent]:
        with self._session_factory() as session:
            repository = AgentRunRepository(session)
            if repository.get_run(run_id) is None:
                raise self._not_found()
            return [self._event_from_record(row) for row in repository.list_events(run_id)]

    async def subscribe(self, run_id: str) -> asyncio.Queue[AgentEvent | None]:
        await self.get(run_id)
        queue: asyncio.Queue[AgentEvent | None] = asyncio.Queue(maxsize=self._queue_size)
        self._subscribers.setdefault(run_id, []).append(queue)
        return queue

    async def unsubscribe(self, run_id: str, queue: asyncio.Queue[AgentEvent | None]) -> None:
        subscribers = self._subscribers.get(run_id)
        if subscribers and queue in subscribers:
            subscribers.remove(queue)
        if not subscribers:
            self._subscribers.pop(run_id, None)

    async def cleanup_expired(self) -> int:
        return 0

    async def recover_interrupted_runs(self) -> int:
        recovered_events: list[AgentEvent] = []
        now = datetime.now(timezone.utc)
        with self._session_factory() as session, session.begin():
            repository = AgentRunRepository(session)
            for run in repository.list_interrupted_runs():
                state = RecruitmentDecisionState.model_validate(run.state_json)
                snapshot = RecruitmentRunSnapshot.model_validate(run.snapshot_json)
                failed_node = snapshot.current_node or state.current_node or "recruitment_strategy"
                error = AgentErrorInfo(
                    code="AGENT_RUN_INTERRUPTED_BY_RESTART",
                    message="后端进程在 Agent Run 执行期间重启，本次运行已停止。",
                    retriable=True,
                    details={"failed_node": failed_node, "failed_step": "process_restart"},
                )
                snapshot.status = AgentRunStatus.FAILED
                snapshot.current_agent = failed_node
                snapshot.current_node = failed_node
                snapshot.error = error
                if snapshot.nodes.get(failed_node) is AgentNodeStatus.RUNNING:
                    snapshot.nodes[failed_node] = AgentNodeStatus.FAILED
                state.status = AgentRunStatus.FAILED
                state.current_agent = failed_node
                state.current_node = failed_node
                state.error = error
                if state.node_statuses.get(failed_node) is AgentNodeStatus.RUNNING:
                    state.node_statuses[failed_node] = AgentNodeStatus.FAILED
                run.status = AgentRunStatus.FAILED.value
                run.current_agent = failed_node
                run.current_node = failed_node
                run.terminal = True
                run.completed_at = now
                run.updated_at = now
                run.error_json = error.model_dump(mode="json")
                run.snapshot_json = _persistence_json(snapshot.model_dump(mode="json", exclude={"events"}))
                run.state_json = _persistence_json(state.model_dump(mode="json", exclude={"events"}))
                self._sync_nodes(repository, run.run_id, snapshot, now)
                for tool_call in repository.list_open_tool_calls(run.run_id):
                    tool_call.status = "FAILED"
                    tool_call.error_json = error.model_dump(mode="json")
                    tool_call.updated_at = now
                event = AgentEvent(
                    event_id=uuid4().hex,
                    run_id=run.run_id,
                    trace_id=run.trace_id,
                    agent_name=failed_node,
                    node_name=failed_node,
                    display_name="Agent Run 因后端重启而中断",
                    event_type=AgentEventType.WORKFLOW_FAILED,
                    status=AgentNodeStatus.FAILED,
                    summary={"failed_node": failed_node, "failed_step": "process_restart"},
                    fallback_used=False,
                    created_at=now,
                    error=error,
                )
                repository.add_event(self._event_record(event, repository.next_sequence(run.run_id)))
                recovered_events.append(event)
        for event in recovered_events:
            self._notify(event.run_id, event)
        return len(recovered_events)

    async def aclose(self) -> None:
        for queues in self._subscribers.values():
            for queue in queues:
                self._put_bounded(queue, None)
        self._subscribers.clear()
        self._run_locks.clear()

    def _record(self, run: AgentRun, rows: list[AgentEventRecord]) -> RecruitmentRunRecord:
        events = [self._event_from_record(row) for row in rows]
        state = RecruitmentDecisionState.model_validate(run.state_json)
        snapshot = RecruitmentRunSnapshot.model_validate(run.snapshot_json)
        state.events = [event.model_copy(deep=True) for event in events]
        snapshot.events = [event.model_copy(deep=True) for event in events]
        snapshot.updated_at = run.updated_at
        return RecruitmentRunRecord(
            run_id=run.run_id,
            owner_user_id=run.owner_user_id,
            state=state,
            snapshot=snapshot,
            events=events,
            created_at=run.created_at,
            updated_at=run.updated_at,
            terminal=run.terminal,
        )

    @staticmethod
    def _sync_nodes(
        repository: AgentRunRepository,
        run_id: str,
        snapshot: RecruitmentRunSnapshot,
        now: datetime,
    ) -> None:
        for node_name, status in snapshot.nodes.items():
            node = repository.get_node(run_id, node_name)
            if node is None:
                node = AgentRunNode(run_id=run_id, node_name=node_name, status=status.value, attempt=1)
                repository.add_node(node)
            node.status = status.value
            if status is AgentNodeStatus.RUNNING and node.started_at is None:
                node.started_at = now
            if status in {
                AgentNodeStatus.COMPLETED,
                AgentNodeStatus.NEEDS_REVIEW,
                AgentNodeStatus.FAILED,
                AgentNodeStatus.SKIPPED,
            }:
                node.completed_at = node.completed_at or now
            node.updated_at = now

    @staticmethod
    def _sync_node_from_event(repository: AgentRunRepository, event: AgentEvent) -> None:
        if not event.node_name:
            return
        node = repository.get_node(event.run_id, event.node_name)
        if node is None:
            node = AgentRunNode(
                run_id=event.run_id,
                node_name=event.node_name,
                status=event.status.value,
                attempt=1,
            )
            repository.add_node(node)
        if event.event_type is AgentEventType.AGENT_STARTED:
            node.started_at = node.started_at or event.created_at
            node.input_summary_json = _safe_summary(event.summary)
        if event.event_type in NODE_COMPLETION_EVENTS:
            node.output_summary_json = _safe_summary(event.summary)
        if event.error:
            node.error_json = event.error.model_dump(mode="json")
        node.status = event.status.value
        if event.status in {
            AgentNodeStatus.COMPLETED,
            AgentNodeStatus.NEEDS_REVIEW,
            AgentNodeStatus.FAILED,
            AgentNodeStatus.SKIPPED,
        }:
            node.completed_at = node.completed_at or event.created_at
        node.updated_at = event.created_at

    @staticmethod
    def _sync_tool_call(repository: AgentRunRepository, event: AgentEvent) -> None:
        if event.event_type is AgentEventType.WORKFLOW_FAILED:
            for tool_call in repository.list_open_tool_calls(event.run_id):
                tool_call.status = "FAILED"
                tool_call.error_json = event.error.model_dump(mode="json") if event.error else {
                    "code": "AGENT_TOOL_INTERRUPTED",
                    "message": "Tool 调用因工作流失败而终止。",
                }
                tool_call.updated_at = event.created_at
            return
        if not event.tool_name:
            return
        if event.event_type is AgentEventType.TOOL_STARTED:
            repository.add_tool_call(AgentToolCall(
                run_id=event.run_id,
                started_event_id=event.event_id,
                node_name=event.node_name,
                tool_name=event.tool_name,
                status="RUNNING",
                input_summary_json=_safe_summary(event.summary),
            ))
            return
        if event.event_type is not AgentEventType.TOOL_COMPLETED:
            return
        tool_call = repository.latest_open_tool_call(event.run_id, event.node_name, event.tool_name)
        if tool_call is None:
            return
        tool_call.completed_event_id = event.event_id
        tool_call.status = "COMPLETED" if event.error is None else "FAILED"
        tool_call.output_summary_json = _safe_summary(event.summary)
        tool_call.duration_ms = event.duration_ms
        tool_call.error_json = event.error.model_dump(mode="json") if event.error else None
        tool_call.updated_at = event.created_at

    @staticmethod
    def _event_record(event: AgentEvent, sequence_no: int) -> AgentEventRecord:
        return AgentEventRecord(
            event_id=event.event_id,
            run_id=event.run_id,
            sequence_no=sequence_no,
            trace_id=event.trace_id,
            candidate_id=event.candidate_id,
            agent_name=event.agent_name,
            node_name=event.node_name,
            display_name=event.display_name,
            event_type=event.event_type.value,
            status=event.status.value,
            summary_json=event.summary,
            tool_name=event.tool_name,
            source_count=event.source_count,
            duration_ms=event.duration_ms,
            fallback_used=event.fallback_used,
            error_json=event.error.model_dump(mode="json") if event.error else None,
            created_at=event.created_at,
        )

    @staticmethod
    def _event_from_record(row: AgentEventRecord) -> AgentEvent:
        return AgentEvent(
            event_id=row.event_id,
            run_id=row.run_id,
            trace_id=row.trace_id,
            candidate_id=row.candidate_id,
            agent_name=row.agent_name,
            node_name=row.node_name,
            display_name=row.display_name,
            event_type=row.event_type,
            status=row.status,
            summary=row.summary_json,
            tool_name=row.tool_name,
            source_count=row.source_count,
            duration_ms=row.duration_ms,
            fallback_used=row.fallback_used,
            created_at=row.created_at,
            error=AgentErrorInfo.model_validate(row.error_json) if row.error_json else None,
        )

    def _notify(self, run_id: str, event: AgentEvent) -> None:
        terminal = event.event_type in TERMINAL_EVENT_TYPES
        for queue in tuple(self._subscribers.get(run_id, [])):
            self._put_bounded(queue, event.model_copy(deep=True))
            if terminal:
                self._put_bounded(queue, None)

    def _lock_for(self, run_id: str) -> asyncio.Lock:
        return self._run_locks.setdefault(run_id, asyncio.Lock())

    @staticmethod
    def _put_bounded(queue: asyncio.Queue[AgentEvent | None], item: AgentEvent | None) -> None:
        if queue.full():
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                return
        queue.put_nowait(item)

    @staticmethod
    def _not_found() -> TalentFlowError:
        return TalentFlowError("AGENT_RUN_NOT_FOUND", "Agent Run 不存在或不可访问。", 404)


def _safe_summary(value: Any, *, depth: int = 0) -> Any:
    if depth > 5:
        return "[TRUNCATED]"
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in list(value.items())[:50]:
            normalized = str(key).casefold()
            if any(marker in normalized for marker in SENSITIVE_KEYS):
                result[str(key)] = "[REDACTED]"
            else:
                result[str(key)] = _safe_summary(item, depth=depth + 1)
        return result
    if isinstance(value, (list, tuple)):
        return [_safe_summary(item, depth=depth + 1) for item in list(value)[:50]]
    if isinstance(value, str):
        return value[:500]
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return str(value)[:500]


def _persistence_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): None if str(key) == "optional_salary_budget" else _persistence_json(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_persistence_json(item) for item in value]
    return value
