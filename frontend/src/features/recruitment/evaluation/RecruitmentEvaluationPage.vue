<template>
  <section class="evaluation-page">
    <header class="evaluation-page__hero">
      <div><span>招聘决策中心</span><h1>多 Agent 招聘评估</h1><p>围绕招聘目标生成策略、企业知识、候选人画像、岗位匹配、决策审查与 HR 建议，确定性评分和最终决定始终保留人工边界。</p></div>
      <div class="phase-badge">PostgreSQL Run · 实时 SSE</div>
    </header>

    <IntegrationStatusPanel
      :health="integrationHealth"
      :loading="healthLoading"
      :error="healthError"
      @refresh="loadIntegrationStatus"
    />

    <PermissionDenied v-if="permissionDenied" description="当前账号缺少 agent.hr.use 权限。" />
    <LoadingState v-else-if="contextLoading" message="正在读取真实岗位与候选人…" />
    <ErrorState v-else-if="contextError" title="招聘上下文加载失败" :message="contextError" retry-label="重新加载" @retry="loadContext" />
    <template v-else>
      <RecruitmentGoalForm :jobs="jobs" :applications="applications" :disabled="runBusy" @submit="start" />
      <div v-if="error" class="evaluation-page__error"><strong>运行提示</strong><span>{{ error }}</span></div>
      <RecruitmentRunOverview :snapshot="snapshot" />
      <div class="evaluation-page__workspace">
        <MultiAgentWorkflowBoard :snapshot="snapshot" :selected-node="selectedNode" @select="selectedNode = $event" />
        <AgentEventFeed :events="events" :streaming="streaming" :status="snapshot?.status" />
      </div>
      <AgentNodeDetail :snapshot="snapshot" :node-name="selectedNode" />
      <Sprint22ResultsPanel :snapshot="snapshot" />
      <Sprint23ResultsPanel :snapshot="snapshot" :candidate-names="candidateNames" />
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ApiClientError } from '../../../shared/api/apiClient';
import { fetchApplications, fetchJobs, type CandidateApplicationListItem } from '../../../shared/api/modules/recruitment';
import { getBackendHealth, type BackendHealth } from '../../../shared/api/modules/health';
import type { Job } from '../../../shared/api/types';
import ErrorState from '../../../shared/components/feedback/ErrorState.vue';
import LoadingState from '../../../shared/components/feedback/LoadingState.vue';
import PermissionDenied from '../../../shared/components/feedback/PermissionDenied.vue';
import AgentEventFeed from './components/AgentEventFeed.vue';
import AgentNodeDetail from './components/AgentNodeDetail.vue';
import IntegrationStatusPanel from './components/IntegrationStatusPanel.vue';
import MultiAgentWorkflowBoard from './components/MultiAgentWorkflowBoard.vue';
import RecruitmentGoalForm from './components/RecruitmentGoalForm.vue';
import RecruitmentRunOverview from './components/RecruitmentRunOverview.vue';
import Sprint22ResultsPanel from './components/Sprint22ResultsPanel.vue';
import Sprint23ResultsPanel from './components/Sprint23ResultsPanel.vue';
import { useRecruitmentAgentRun } from './composables/useRecruitmentAgentRun';

const route = useRoute();
const jobs = ref<Job[]>([]);
const applications = ref<CandidateApplicationListItem[]>([]);
const contextLoading = ref(true);
const contextError = ref('');
const permissionDenied = ref(false);
const selectedNode = ref('recruitment_strategy');
const integrationHealth = ref<BackendHealth | null>(null);
const healthLoading = ref(false);
const healthError = ref('');
const { snapshot, events, loading, streaming, error, isTerminal, start, restore } = useRecruitmentAgentRun();
const runBusy = computed(() => loading.value || Boolean(snapshot.value && !isTerminal.value));
const candidateNames = computed(() => applications.value.reduce<Record<number, string>>((names, application) => {
  if (application.candidate_name) names[application.candidate_id] = application.candidate_name;
  return names;
}, {}));

async function loadContext(): Promise<void> {
  contextLoading.value = true;
  contextError.value = '';
  permissionDenied.value = false;
  try {
    [jobs.value, applications.value] = await Promise.all([fetchJobs(), fetchApplications()]);
  } catch (cause) {
    if (cause instanceof ApiClientError && cause.status === 403) permissionDenied.value = true;
    else contextError.value = cause instanceof Error ? cause.message : '无法读取招聘岗位和候选人。';
  } finally {
    contextLoading.value = false;
  }
}

async function loadIntegrationStatus(): Promise<void> {
  healthLoading.value = true;
  healthError.value = '';
  try {
    integrationHealth.value = await getBackendHealth();
  } catch (cause) {
    integrationHealth.value = null;
    healthError.value = cause instanceof Error ? cause.message : '集成状态暂时无法获取';
  } finally {
    healthLoading.value = false;
  }
}

onMounted(async () => {
  await Promise.all([loadContext(), loadIntegrationStatus()]);
  const queryRunId = route.query.run_id;
  const runId = Array.isArray(queryRunId) ? queryRunId[0] : queryRunId;
  if (typeof runId === 'string' && runId) await restore(runId);
});

watch(() => snapshot.value?.status, (status, previous) => {
  if (status && status !== previous && isTerminal.value) void loadIntegrationStatus();
});
</script>

<style scoped>
.evaluation-page { display:grid; max-width:1600px; margin:0 auto; gap:20px; }.evaluation-page__hero { display:flex; align-items:flex-end; justify-content:space-between; gap:20px; }.evaluation-page__hero span { color:var(--color-primary); font-size:12px; font-weight:900; }.evaluation-page__hero h1 { margin:7px 0; color:var(--color-text); font-size:30px; }.evaluation-page__hero p { margin:0; color:var(--color-muted); }.phase-badge { padding:10px 14px; border:1px solid var(--color-line); border-radius:999px; background:var(--color-surface); color:var(--color-primary); font-weight:800; }.evaluation-page__workspace { display:grid; grid-template-columns:minmax(0,1.35fr) minmax(420px,.8fr); gap:18px; align-items:start; }.evaluation-page__error { display:flex; gap:12px; padding:13px 16px; border:1px solid var(--color-node-failed-border); border-radius:var(--radius-sm); background:var(--color-status-error-bg); color:var(--color-status-error-text); }.evaluation-page__error span { color:var(--color-status-error-text); } @media(max-width:1100px){.evaluation-page__workspace{grid-template-columns:1fr}.evaluation-page__hero{align-items:flex-start;flex-direction:column}} 
</style>

