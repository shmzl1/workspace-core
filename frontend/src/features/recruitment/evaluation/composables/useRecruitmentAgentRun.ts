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
    if (event.event_type === AgentEventType.WORKFLOW_STARTED) current.status = AgentRunStatus.RUNNING;
    if (event.event_type === AgentEventType.AGENT_STARTED) {
      if (event.node_name) current.nodes[event.node_name] = AgentNodeStatus.RUNNING;
      current.current_agent = event.agent_name;
      current.current_node = event.node_name;
      current.current_candidate_id = event.candidate_id;
    }
    if (event.event_type === AgentEventType.AGENT_COMPLETED && event.node_name) {
      current.nodes[event.node_name] = event.status;
    }
    if (event.candidate_id !== null && [
      AgentEventType.TOOL_STARTED,
      AgentEventType.TOOL_COMPLETED,
      AgentEventType.INTERMEDIATE_RESULT,
      AgentEventType.REVIEW_COMPLETED,
    ].includes(event.event_type)) current.current_candidate_id = event.candidate_id;
    if (event.event_type === AgentEventType.PLAN_CREATED) {
      const plan = event.summary.execution_plan;
      if (isExecutionPlan(plan)) current.execution_plan = plan;
    }
    if (event.event_type === AgentEventType.KNOWLEDGE_RETRIEVED) {
      const knowledge = event.summary.knowledge_summary;
      const rubric = event.summary.job_rubric;
      if (knowledge && typeof knowledge === 'object') {
        current.knowledge_summary = knowledge as RecruitmentRunSnapshot['knowledge_summary'];
        current.sources = current.knowledge_summary?.sources || [];
      }
      if (rubric && typeof rubric === 'object') current.job_rubric = rubric as RecruitmentRunSnapshot['job_rubric'];
    }
    if (event.event_type === AgentEventType.INTERMEDIATE_RESULT) {
      const profile = event.summary.candidate_profile;
      if (profile && typeof profile === 'object' && event.candidate_id !== null) {
        current.candidate_profiles[String(event.candidate_id)] = profile as RecruitmentRunSnapshot['candidate_profiles'][string];
      }
      const jobMatch = event.summary.job_match_summary;
      if (jobMatch && typeof jobMatch === 'object' && event.candidate_id !== null) {
        current.job_matches[String(event.candidate_id)] = jobMatch as RecruitmentRunSnapshot['job_matches'][string];
      }
    }
    if (event.event_type === AgentEventType.REVIEW_COMPLETED) {
      const decisionReview = event.summary.decision_review;
      if (decisionReview && typeof decisionReview === 'object' && event.candidate_id !== null) {
        current.decision_reviews[String(event.candidate_id)] = decisionReview as RecruitmentRunSnapshot['decision_reviews'][string];
      }
    }
    if (event.event_type === AgentEventType.REPORT_GENERATED) {
      const report = event.summary.report;
      if (report && typeof report === 'object') {
        current.report = report as RecruitmentRunSnapshot['report'];
      }
    }
    if (event.event_type === AgentEventType.AGENT_COMPLETED) current.current_candidate_id = null;
    if (event.event_type === AgentEventType.CANDIDATE_COMPLETED) {
      const completed = event.summary.completed_candidates;
      if (typeof completed === 'number') current.completed_candidates = completed;
      current.current_candidate_id = null;
    }
    if (event.event_type === AgentEventType.WORKFLOW_COMPLETED) {
      current.status = AgentRunStatus.COMPLETED;
      current.current_agent = null;
      current.current_node = null;
      current.current_candidate_id = null;
      const skipped = event.summary.skipped_nodes;
      if (Array.isArray(skipped)) {
        for (const node of skipped) if (typeof node === 'string') current.nodes[node] = AgentNodeStatus.SKIPPED;
      }
    }
    if (event.event_type === AgentEventType.WORKFLOW_FAILED) {
      current.status = AgentRunStatus.FAILED;
      const failedNode = event.node_name ?? current.current_node;
      if (failedNode) current.nodes[failedNode] = AgentNodeStatus.FAILED;
      current.current_agent = event.agent_name ?? current.current_agent;
      current.current_node = failedNode;
      current.current_candidate_id = event.candidate_id;
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
    return '未找到该运行记录，或当前账号无权访问。';
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
