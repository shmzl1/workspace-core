"""Database access for Agent Runtime persistence."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.agent_runtime.models import (
    AgentEventRecord,
    AgentRun,
    AgentRunNode,
    AgentToolCall,
)


class AgentRunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_run(self, run: AgentRun) -> None:
        self.session.add(run)

    def get_run(self, run_id: str, *, for_update: bool = False) -> AgentRun | None:
        statement = select(AgentRun).where(AgentRun.run_id == run_id)
        if for_update:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def get_owned(self, run_id: str, owner_user_id: int) -> AgentRun | None:
        return self.session.scalar(
            select(AgentRun).where(
                AgentRun.run_id == run_id,
                AgentRun.owner_user_id == owner_user_id,
            )
        )

    def list_events(self, run_id: str) -> list[AgentEventRecord]:
        return list(
            self.session.scalars(
                select(AgentEventRecord)
                .where(AgentEventRecord.run_id == run_id)
                .order_by(AgentEventRecord.sequence_no)
            )
        )

    def next_sequence(self, run_id: str) -> int:
        current = self.session.scalar(
            select(func.max(AgentEventRecord.sequence_no)).where(AgentEventRecord.run_id == run_id)
        )
        return int(current or 0) + 1

    def add_event(self, event: AgentEventRecord) -> None:
        self.session.add(event)

    def get_node(self, run_id: str, node_name: str, attempt: int = 1) -> AgentRunNode | None:
        return self.session.scalar(
            select(AgentRunNode).where(
                AgentRunNode.run_id == run_id,
                AgentRunNode.node_name == node_name,
                AgentRunNode.attempt == attempt,
            )
        )

    def add_node(self, node: AgentRunNode) -> None:
        self.session.add(node)

    def latest_open_tool_call(
        self,
        run_id: str,
        node_name: str | None,
        tool_name: str,
    ) -> AgentToolCall | None:
        return self.session.scalar(
            select(AgentToolCall)
            .where(
                AgentToolCall.run_id == run_id,
                AgentToolCall.node_name == node_name,
                AgentToolCall.tool_name == tool_name,
                AgentToolCall.status == "RUNNING",
            )
            .order_by(AgentToolCall.id.desc())
            .limit(1)
        )

    def add_tool_call(self, tool_call: AgentToolCall) -> None:
        self.session.add(tool_call)

    def list_open_tool_calls(self, run_id: str) -> list[AgentToolCall]:
        return list(
            self.session.scalars(
                select(AgentToolCall).where(
                    AgentToolCall.run_id == run_id,
                    AgentToolCall.status == "RUNNING",
                )
            )
        )

    def list_interrupted_runs(self) -> list[AgentRun]:
        return list(
            self.session.scalars(
                select(AgentRun)
                .where(AgentRun.status.in_(["PENDING", "RUNNING"]), AgentRun.terminal.is_(False))
                .with_for_update()
            )
        )
