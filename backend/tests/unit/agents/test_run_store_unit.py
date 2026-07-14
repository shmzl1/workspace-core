import asyncio
import functools
from datetime import date, datetime, timedelta, timezone

import pytest

from app.agents.runtime.run_store import ApplicationAgentRunStore, InMemoryAgentRunStore
from app.agents.shared import AgentEvent, AgentEventType, AgentNodeStatus, AgentRunStatus
from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentDecisionState,
    RecruitmentGoal,
    RecruitmentJobContext,
    RecruitmentRunContext,
    RecruitmentRunRequest,
    RecruitmentRunSnapshot,
)
from app.core.exceptions import TalentFlowError


def models(run_id: str) -> tuple[RecruitmentDecisionState, RecruitmentRunSnapshot]:
    goal = RecruitmentGoal(job_id=1, job_title="Backend Engineer", department="R&D", target_headcount=1)
    job = RecruitmentJobContext(
        job_id=1,
        job_code="BACKEND-001",
        job_title=goal.job_title,
        department=goal.department,
        status="OPEN",
        source_version="test-v1",
        effective_date=date(2026, 7, 14),
    )
    context = RecruitmentRunContext(request=RecruitmentRunRequest(goal=goal), job=job)
    now = datetime.now(timezone.utc)
    state = RecruitmentDecisionState(
        run_id=run_id,
        trace_id=f"trace-{run_id}",
        actor_user_id=1,
        context=context,
    )
    snapshot = RecruitmentRunSnapshot(
        run_id=run_id,
        trace_id=state.trace_id,
        status=AgentRunStatus.PENDING,
        goal=goal,
        job=job,
        created_at=now,
        updated_at=now,
    )
    return state, snapshot


def event(run_id: str, event_id: str, event_type: AgentEventType = AgentEventType.AGENT_STARTED) -> AgentEvent:
    return AgentEvent(
        event_id=event_id,
        run_id=run_id,
        trace_id=f"trace-{run_id}",
        display_name="test event",
        event_type=event_type,
        status=AgentNodeStatus.COMPLETED,
        created_at=datetime.now(timezone.utc),
    )


async def create_run(store: InMemoryAgentRunStore, run_id: str = "run-1", owner: int = 1) -> None:
    state, snapshot = models(run_id)
    await store.create(owner, state, snapshot)


def run_async_test(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        return asyncio.run(function(*args, **kwargs))

    return wrapper


@run_async_test
async def test_missing_and_other_owner_runs_are_not_accessible() -> None:
    store = InMemoryAgentRunStore()
    with pytest.raises(TalentFlowError, match="不存在") as missing:
        await store.get("missing")
    assert missing.value.code == "AGENT_RUN_NOT_FOUND"

    await create_run(store, owner=7)
    with pytest.raises(TalentFlowError) as foreign:
        await store.get_owned("run-1", owner_user_id=8)
    assert foreign.value.code == "AGENT_RUN_NOT_FOUND"


@run_async_test
async def test_capacity_replaces_terminal_run_and_rejects_active_run_capacity() -> None:
    store = InMemoryAgentRunStore(max_runs=1)
    await create_run(store, "active")
    state, snapshot = models("blocked")
    with pytest.raises(TalentFlowError, match="上限") as error:
        await store.create(1, state, snapshot)
    assert error.value.code == "AGENT_RUN_CAPACITY_REACHED"

    await store.update_snapshot("active", models("active")[1], terminal=True)
    await store.create(1, state, snapshot)
    with pytest.raises(TalentFlowError):
        await store.get("active")
    assert (await store.get("blocked")).run_id == "blocked"


@run_async_test
async def test_event_limit_subscription_close_and_unsubscribe_behaviors() -> None:
    store = InMemoryAgentRunStore(max_events_per_run=2)
    await create_run(store)
    queue = await store.subscribe("run-1")
    unrelated_queue: asyncio.Queue[AgentEvent | None] = asyncio.Queue()
    await store.unsubscribe("not-a-run", unrelated_queue)

    await store.append_event("run-1", event("run-1", "one"))
    await store.append_event("run-1", event("run-1", "two"))
    await store.append_event("run-1", event("run-1", "three"))
    await store.append_event("run-1", event("run-1", "done", AgentEventType.WORKFLOW_COMPLETED))

    assert [item.event_id for item in await store.history("run-1")] == ["three", "done"]
    received = [await queue.get(), await queue.get()]
    assert received[-1] is None
    assert (await store.get("run-1")).terminal is True

    await store.unsubscribe("run-1", queue)
    await store.append_event("run-1", event("run-1", "after-unsubscribe"))
    assert queue.empty()


@run_async_test
async def test_cleanup_and_returned_values_do_not_leak_internal_state() -> None:
    store = InMemoryAgentRunStore(terminal_ttl=timedelta(seconds=1))
    await create_run(store)
    returned = await store.get("run-1")
    returned.snapshot.goal.job_title = "mutated outside"
    returned.state.context.job.job_title = "also mutated"
    await store.append_event("run-1", event("run-1", "copied"))
    history = await store.history("run-1")
    history[0].summary["changed"] = True

    stored = await store.get("run-1")
    assert stored.snapshot.goal.job_title == "Backend Engineer"
    assert stored.state.context.job.job_title == "Backend Engineer"
    assert "changed" not in (await store.history("run-1"))[0].summary

    await store.update_snapshot("run-1", stored.snapshot, terminal=True)
    store._runs["run-1"].updated_at = datetime.now(timezone.utc) - timedelta(seconds=2)
    assert await store.cleanup_expired() == 1
    with pytest.raises(TalentFlowError):
        await store.history("run-1")


@run_async_test
async def test_concurrent_run_and_event_operations_are_isolated() -> None:
    store = InMemoryAgentRunStore(max_runs=16, max_events_per_run=20)
    run_ids = [f"concurrent-{index}" for index in range(8)]

    async def create_and_append(run_id: str) -> None:
        await create_run(store, run_id, owner=1)
        await asyncio.gather(*(store.append_event(run_id, event(run_id, f"{run_id}-{index}")) for index in range(6)))

    await asyncio.gather(*(create_and_append(run_id) for run_id in run_ids))
    records = await asyncio.gather(*(store.get(run_id) for run_id in run_ids))
    assert all(len(record.events) == 6 for record in records)
    assert all({item.run_id for item in record.events} == {record.run_id} for record in records)


@run_async_test
async def test_close_and_application_proxy_delegate_all_store_operations(monkeypatch: pytest.MonkeyPatch) -> None:
    store = InMemoryAgentRunStore()
    await create_run(store)
    queue = await store.subscribe("run-1")
    await store.aclose()
    assert await queue.get() is None
    assert await store.recover_interrupted_runs() == 0

    proxy = ApplicationAgentRunStore()
    monkeypatch.setattr(ApplicationAgentRunStore, "_store", staticmethod(lambda: store))
    state, snapshot = models("proxy")
    await proxy.create(1, state, snapshot)
    assert (await proxy.get("proxy")).run_id == "proxy"
    assert (await proxy.get_owned("proxy", 1)).run_id == "proxy"
    await proxy.update_snapshot("proxy", snapshot, terminal=False)
    await proxy.append_event("proxy", event("proxy", "event"))
    assert len(await proxy.history("proxy")) == 1
    proxy_queue = await proxy.subscribe("proxy")
    await proxy.unsubscribe("proxy", proxy_queue)
    assert await proxy.cleanup_expired() == 0
    assert await proxy.recover_interrupted_runs() == 0
    await proxy.aclose()
