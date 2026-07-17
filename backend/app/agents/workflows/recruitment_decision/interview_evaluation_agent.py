"""Static contract for the not-yet-implemented interview evaluation node."""

from collections.abc import Mapping

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.runtime.recruitment_support import (
    INTERVIEW_NODE_NAME,
    INTERVIEW_SKIP_REASON,
    RecruitmentNodeExecution,
    event,
    execute_recruitment_node,
    publish,
)
from app.agents.runtime.run_store import AgentRunStore, RecruitmentRunRecord
from app.agents.shared import AgentEventType, AgentNodeContract, AgentNodeStatus

INTERVIEW_EVALUATION_NODE = AgentNodeContract(
    name="interview_evaluation",
    display_name="面试评估 Agent",
    responsibility="仅在存在真实结构化面试数据时生成评价；否则标记待面试。",
    required_inputs=("execution_plan", "interview_data"),
    dependencies=("recruitment_strategy",),
    allowed_tools=("interview_read_service",),
    output_fields=("interview_evaluations",),
    forbidden_behaviors=("伪造面试数据", "自动确认面试排期", "替代 HR 做录用决定"),
    can_skip=True,
)


async def interview_evaluation_node(
    graph_state: Mapping[str, object],
    *,
    store: AgentRunStore,
    dependencies: RecruitmentRunnerDependencies,
) -> dict[str, object]:
    """Enter the real Graph node and preserve the existing truthful skip."""

    run_id = str(graph_state["run_id"])

    async def execute(
        record: RecruitmentRunRecord,
        _execution: RecruitmentNodeExecution,
    ) -> dict[str, object]:
        snapshot = record.snapshot
        state = record.state
        snapshot.current_agent = INTERVIEW_NODE_NAME
        snapshot.current_node = INTERVIEW_NODE_NAME
        snapshot.nodes[INTERVIEW_NODE_NAME] = AgentNodeStatus.SKIPPED
        state.current_agent = INTERVIEW_NODE_NAME
        state.current_node = INTERVIEW_NODE_NAME
        state.node_statuses[INTERVIEW_NODE_NAME] = AgentNodeStatus.SKIPPED
        await store.update_snapshot(run_id, snapshot, state)
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, AgentNodeStatus.SKIPPED,
            "面试评估 Agent 已跳过",
            {
                "skip_reason": INTERVIEW_SKIP_REASON,
                "structured_interview_feedback_available": False,
                "interview_conclusion_generated": False,
                "next_action": "决策审查将缺少真实面试评价标记为待人工补充",
            },
            agent_name=INTERVIEW_NODE_NAME, node_name=INTERVIEW_NODE_NAME,
        ))
        return {}

    return await execute_recruitment_node(
        run_id,
        store,
        dependencies,
        INTERVIEW_NODE_NAME,
        "skip_interview_evaluation",
        execute,
    )

