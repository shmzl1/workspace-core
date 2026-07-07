"""Shared Agent state skeleton."""

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    trace_id: str
    actor_id: str | None = None
    messages: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
