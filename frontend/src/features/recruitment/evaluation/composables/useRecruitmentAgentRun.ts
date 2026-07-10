import { computed, onBeforeUnmount, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ApiClientError } from '../../../../shared/api/apiClient';
import {
  createRecruitmentRun,
  getRecruitmentRun,
  subscribeRecruitmentRunEvents,
} from '../../../../shared/api/modules/agent';
import {
  AgentEventType,
  AgentNodeStatus,
  AgentRunStatus,
  type AgentEvent,
  type RecruitmentExecutionPlan,
  type RecruitmentRunRequest,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';

export function useRecruitmentAgentRun() {
  const route = useRoute();
  const router = useRouter();
  const snapshot = ref<RecruitmentRunSnapshot | null>(null);
  const events = ref<AgentEvent[]>([]);
  const loading = ref(false);
  const streaming = ref(false);
  const error = ref('');
  let controller: AbortController | null = null;

  const isTerminal = computed(() =>
    snapshot.value !== null && [
      AgentRunStatus.COMPLETED,
      AgentRunStatus.FAILED,
      AgentRunStatus.CANCELLED,
    ].includes(snapshot.value.status),
  );

  async function start(payload: RecruitmentRunRequest): Promise<void> {
    stopSubscription();
    loading.value = true;
    error.value = '';
    snapshot.value = null;
    events.value = [];
    try {
      const created = await createRecruitmentRun(payload);
      setSnapshot(created);
      await router.replace({ query: { ...route.query, run_id: created.run_id } });
      if (!isTerminal.value) void connect(created.run_id);
    } catch (cause) {
      error.value = errorMessage(cause);
    } finally {
      loading.value = false;
    }
  }

  async function restore(runId: string): Promise<void> {
    if (!runId) return;
    stopSubscription();
    loading.value = true;
    error.value = '';
    try {
      const restored = await getRecruitmentRun(runId);
      setSnapshot(restored);
      if (!isTerminal.value) void connect(runId);
    } catch (cause) {
      snapshot.value = null;
      events.value = [];
      error.value = errorMessage(cause);
    } finally {
      loading.value = false;
    }
  }

  async function refresh(): Promise<void> {
    const runId = snapshot.value?.run_id;
    if (!runId) return;
    try {
      setSnapshot(await getRecruitmentRun(runId));
    } catch (cause) {
      error.value = errorMessage(cause);
    }
  }

  async function connect(runId: string): Promise<void> {
    stopSubscription();
    const activeController = new AbortController();
    controller = activeController;
    streaming.value = true;
    try {
      await subscribeRecruitmentRunEvents(
        runId,
        {
          onEvent: applyEvent,
          onComplete: () => { void refresh(); },
          onError: (streamError) => { error.value = streamError.message; },
        },
        activeController.signal,
      );
    } catch (cause) {
      if (!activeController.signal.aborted) error.value = errorMessage(cause);
    } finally {
      if (controller === activeController) {
        controller = null;
        streaming.value = false;
      }
    }
  }

  function applyEvent(event: AgentEvent): void {
    if (events.value.some((item) => item.event_id === event.event_id)) return;
    events.value = [...events.value, event];
    const current = snapshot.value;
    if (!current) return;
    current.events = events.value;
    current.updated_at = event.created_at;
    if (event.node_name) current.nodes[event.node_name] = event.status;
    if (event.event_type === AgentEventType.WORKFLOW_STARTED) current.status = AgentRunStatus.RUNNING;
    if (event.event_type === AgentEventType.AGENT_STARTED) {
      current.current_agent = event.agent_name;
      current.current_node = event.node_name;
    }
    if (event.event_type === AgentEventType.PLAN_CREATED) {
      const plan = event.summary.execution_plan;
      if (isExecutionPlan(plan)) current.execution_plan = plan;
    }
    if (event.event_type === AgentEventType.WORKFLOW_COMPLETED) {
      current.status = AgentRunStatus.COMPLETED;
      current.current_agent = null;
      current.current_node = null;
      const skipped = event.summary.skipped_nodes;
      if (Array.isArray(skipped)) {
        for (const node of skipped) if (typeof node === 'string') current.nodes[node] = AgentNodeStatus.SKIPPED;
      }
    }
    if (event.event_type === AgentEventType.WORKFLOW_FAILED) {
      current.status = AgentRunStatus.FAILED;
      current.error = event.error;
    }
  }

  function setSnapshot(value: RecruitmentRunSnapshot): void {
    snapshot.value = value;
    const unique = new Map(value.events.map((event) => [event.event_id, event]));
    events.value = [...unique.values()];
  }

  function stopSubscription(): void {
    controller?.abort();
    controller = null;
    streaming.value = false;
  }

  onBeforeUnmount(stopSubscription);

  return {
    snapshot,
    events,
    loading,
    streaming,
    error,
    isTerminal,
    start,
    restore,
    refresh,
    stopSubscription,
  };
}

function errorMessage(cause: unknown): string {
  if (cause instanceof ApiClientError && cause.code === 'AGENT_RUN_NOT_FOUND') {
    return '本次运行记录仅保存在当前后端进程中，请重新发起。';
  }
  return cause instanceof Error ? cause.message : '招聘策略运行请求失败。';
}

function isExecutionPlan(value: unknown): value is RecruitmentExecutionPlan {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<RecruitmentExecutionPlan>;
  return Array.isArray(candidate.required_nodes)
    && Array.isArray(candidate.skipped_nodes)
    && Array.isArray(candidate.plan_notes)
    && typeof candidate.candidate_count === 'number';
}
