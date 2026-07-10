<template>
  <section class="run-overview">
    <header>
      <div><span>总体运行状态</span><h2>真实 Agent Run</h2></div>
      <strong>{{ snapshot?.status || 'WAITING' }}</strong>
    </header>
    <div class="run-overview__grid">
      <article><span>招聘目标</span><strong>{{ goalSummary }}</strong></article>
      <article><span>当前岗位</span><strong>{{ jobSummary }}</strong></article>
      <article><span>候选人进度</span><strong>{{ candidateProgress }}</strong></article>
      <article><span>当前候选人</span><strong>{{ currentCandidate }}</strong></article>
      <article><span>当前 Agent</span><strong>{{ currentAgent }}</strong></article>
      <article><span>阶段进度</span><strong>{{ phaseProgress }}</strong></article>
      <article><span>真实运行耗时</span><strong>{{ elapsed }}</strong></article>
      <article><span>当前范围</span><strong>SPRINT_2_2_STRATEGY_RESUME_KNOWLEDGE</strong></article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import {
  AgentNodeStatus,
  AgentRunStatus,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';

const props = defineProps<{ snapshot: RecruitmentRunSnapshot | null }>();
const now = ref(Date.now());
let timer: ReturnType<typeof setInterval> | null = null;

const agentLabels: Record<string, string> = {
  recruitment_strategy: '招聘策略 Agent',
  resume_parser: '简历解析 Agent',
  job_match: '岗位匹配 Agent',
  interview_evaluation: '面试评估 Agent',
  decision_review: '决策审查 Agent',
  hr_report: 'HR 最终报告',
};

const goalSummary = computed(() => {
  const goal = props.snapshot?.goal;
  if (!goal) return '等待创建真实 Run';
  return `${goal.job_title} · 目标 ${goal.target_headcount} 人`;
});
const jobSummary = computed(() => {
  const job = props.snapshot?.job;
  return job ? `${job.department} · ${job.job_title}（${job.job_code}）` : '等待岗位上下文';
});
const candidateProgress = computed(() => {
  const snapshot = props.snapshot;
  return snapshot ? `${snapshot.completed_candidates} / ${snapshot.total_candidates}` : '0 / 0';
});
const currentCandidate = computed(() => {
  const candidateId = props.snapshot?.current_candidate_id;
  if (candidateId) return `候选人 #${candidateId}`;
  if (props.snapshot?.completed_candidates === props.snapshot?.total_candidates && props.snapshot?.total_candidates) {
    return '当前阶段候选人解析已结束';
  }
  return '等待候选人解析';
});
const currentAgent = computed(() => {
  const agent = props.snapshot?.current_agent;
  if (agent) return agentLabels[agent] || agent;
  return props.snapshot?.status === AgentRunStatus.COMPLETED ? '当前阶段已结束' : '等待运行';
});
const phaseProgress = computed(() => {
  const nodes = props.snapshot?.nodes;
  const statuses = [nodes?.recruitment_strategy, nodes?.resume_parser];
  const completed = statuses.filter((status) => status === AgentNodeStatus.COMPLETED).length;
  if (statuses.some((status) => status === AgentNodeStatus.FAILED)) return `${completed} / 2（失败）`;
  if (statuses.some((status) => status === AgentNodeStatus.RUNNING)) return `${completed} / 2（执行中）`;
  return `${completed} / 2（${completed === 2 ? '100%' : '等待'}）`;
});
const elapsed = computed(() => {
  const snapshot = props.snapshot;
  if (!snapshot) return '0.0 s';
  const start = Date.parse(snapshot.created_at);
  const terminal = [AgentRunStatus.COMPLETED, AgentRunStatus.FAILED, AgentRunStatus.CANCELLED]
    .includes(snapshot.status);
  const end = terminal ? Date.parse(snapshot.updated_at) : now.value;
  const milliseconds = Number.isFinite(start) && Number.isFinite(end) ? Math.max(0, end - start) : 0;
  return `${(milliseconds / 1000).toFixed(1)} s`;
});

onMounted(() => { timer = setInterval(() => { now.value = Date.now(); }, 1000); });
onBeforeUnmount(() => { if (timer) clearInterval(timer); });
</script>

<style scoped>
.run-overview { display:grid; gap:16px; padding:20px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:#fff; box-shadow:var(--shadow-card); }
.run-overview header { display:flex; align-items:flex-end; justify-content:space-between; gap:16px; }
.run-overview header span { color:var(--color-primary); font-size:12px; font-weight:800; }
.run-overview h2 { margin:5px 0 0; }
.run-overview header strong { color:var(--color-muted); font-size:12px; }
.run-overview__grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }
.run-overview article { min-width:0; padding:12px; border-radius:12px; background:var(--color-surface-soft); }
.run-overview article span,.run-overview article strong { display:block; }
.run-overview article span { color:var(--color-subtle); font-size:11px; }
.run-overview article strong { overflow:hidden; margin-top:6px; color:var(--color-text); font-size:13px; text-overflow:ellipsis; }
@media(max-width:1000px){.run-overview__grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:560px){.run-overview__grid{grid-template-columns:1fr}}
</style>
