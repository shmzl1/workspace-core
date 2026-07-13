"""SSE replay and subscription for real AgentEvent instances."""

import asyncio
from collections.abc import AsyncIterator

from fastapi import Request
from fastapi.responses import StreamingResponse

from app.agents.runtime.run_store import AgentRunStore
from app.agents.shared import AgentEvent, AgentEventType

HEARTBEAT_SECONDS = 15.0
TERMINAL_EVENTS = {AgentEventType.WORKFLOW_COMPLETED, AgentEventType.WORKFLOW_FAILED}


def format_sse_event(event: AgentEvent) -> str:
    return (
        f"id: {event.event_id}\n"
        "event: agent_event\n"
        f"data: {event.model_dump_json()}\n\n"
    )


def create_agent_event_stream(
    request: Request,
    run_id: str,
    owner_user_id: int,
    store: AgentRunStore,
) -> StreamingResponse:
    async def stream() -> AsyncIterator[str]:
        queue = await store.subscribe(run_id)
        sent_event_ids: set[str] = set()
        try:
            await store.get_owned(run_id, owner_user_id)
            for event in await store.history(run_id):
                if event.event_id in sent_event_ids:
                    continue
                sent_event_ids.add(event.event_id)
                yield format_sse_event(event)
            record = await store.get_owned(run_id, owner_user_id)
            if record.terminal:
                for event in await store.history(run_id):
                    if event.event_id in sent_event_ids:
                        continue
                    sent_event_ids.add(event.event_id)
                    yield format_sse_event(event)
                return
            while True:
                if await request.is_disconnected():
                    return
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_SECONDS)
                except TimeoutError:
                    yield ": heartbeat\n\n"
                    continue
                if event is None:
                    return
                if event.event_id in sent_event_ids:
                    continue
                sent_event_ids.add(event.event_id)
                yield format_sse_event(event)
                if event.event_type in TERMINAL_EVENTS:
                    return
        finally:
            await store.unsubscribe(run_id, queue)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
