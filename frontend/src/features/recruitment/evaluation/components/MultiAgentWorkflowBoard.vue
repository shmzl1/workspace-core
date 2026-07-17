<template>
  <section class="recruitment-hover-card workflow-board bg-white rounded-3xl shadow-sm border border-slate-200 p-8 space-y-6">
    <div class="workflow-board__header border-b border-slate-100 pb-4">
      <div>
        <h2 class="text-lg font-bold flex items-center gap-2 text-slate-900">
          <span class="w-1.5 h-6 bg-indigo-500 rounded-full"></span>
          顶层工作流执行链路
        </h2>
        <p class="mt-1.5 text-xs text-slate-500">Agent 按招聘评估链路分阶段执行</p>
      </div>
      <div class="workflow-legend" aria-label="工作流状态图例">
        <span><i class="legend-dot legend-dot--completed"></i>已完成</span>
        <span><i class="legend-dot legend-dot--running"></i>运行中</span>
        <span><i class="legend-dot legend-dot--review"></i>需要复核</span>
      </div>
    </div>

    <div class="workflow-canvas">
      <div class="workflow-track">
        <template v-for="(stage, stageIndex) in workflowStages" :key="stage.key">
          <div
            class="workflow-stage"
            :class="stage.groupLabel ? 'workflow-stage--group' : 'workflow-stage--single'"
          >
            <span v-if="stage.groupLabel" class="workflow-stage__label">{{ stage.groupLabel }}</span>
            <div class="workflow-stage__nodes">
              <button
                v-for="node in stage.nodes"
                :key="node.name"
                type="button"
                class="workflow-node"
                :class="[
                  isNodeExpanded(node.name) ? 'workflow-node--expanded' : 'workflow-node--compact',
                  `workflow-node--${nodeStatus(node.name).toLowerCase()}`,
                  selectedNode === node.name ? 'workflow-node--selected' : '',
                ]"
                title="点击查看处理依据"
                :aria-label="`查看${node.title}处理依据`"
                @click="emit('select', node.name)"
              >
                <div class="workflow-node__main">
                  <span class="workflow-node__icon" aria-hidden="true">
                    <component :is="nodeIcon(nodeStatus(node.name))" />
                  </span>
                  <div class="workflow-node__heading">
                    <strong>{{ node.title }}</strong>
                    <span :class="`node-status node-status--${nodeStatus(node.name).toLowerCase()}`">
                      {{ nodeStatusLabel(nodeStatus(node.name)) }}
                    </span>
                  </div>
                </div>

                <Transition name="node-details">
                  <div v-if="isNodeExpanded(node.name)" class="workflow-node__details">
                    <p class="workflow-node__subtitle">
                      {{ node.name === 'recruitment_strategy' ? strategySubtitle : node.subtitle }}
                    </p>
                    <AgentTaskInstanceList :instances="nodeInstances(node.name)" />
                    <p class="workflow-node__count">{{ instanceCountLabel(node.name) }}</p>
                  </div>
                </Transition>
              </button>
            </div>
          </div>

          <div
            v-if="stageIndex < workflowStages.length - 1"
            class="workflow-connector"
            :class="stageConnectorClass(stage, workflowStages[stageIndex + 1])"
            aria-hidden="true"
          >
            <span class="workflow-connector__line"></span>
            <span class="workflow-connector__arrow"></span>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h } from 'vue';
import {
  AgentEventType,
  AgentNodeStatus,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';
import AgentTaskInstanceList from './AgentTaskInstanceList.vue';
import {
  buildCandidateTaskInstances,
  buildSingletonTaskInstance,
  hasNodeActivity,
  type AgentTaskInstance,
} from '../utils/agentTaskInstances';

interface WorkflowNodeDefinition {
  name: string;
  title: string;
  subtitle: string;
  countNoun: string;
  candidateLevel: boolean;
}

interface WorkflowStage {
  key: string;
  groupLabel: string | null;
  nodes: WorkflowNodeDefinition[];
}

const props = withDefaults(defineProps<{
  snapshot: RecruitmentRunSnapshot | null;
  selectedNode?: string;
  candidateNames?: Record<number, string>;
}>(), {
  selectedNode: '',
  candidateNames: () => ({}),
});

const emit = defineEmits<{ select: [nodeName: string] }>();

const definitions: WorkflowNodeDefinition[] = [
  {
    name: 'recruitment_strategy',
    title: '招聘策略 Agent',
    subtitle: '规划招聘目标与执行步骤',
    countNoun: '策略规划实例',
    candidateLevel: false,
  },
  {
    name: 'resume_parser',
    title: '简历解析 Agent',
    subtitle: '结构化提取候选人画像',
    countNoun: '解析任务实例',
    candidateLevel: true,
  },
  {
    name: 'job_match',
    title: '岗位匹配 Agent',
    subtitle: '逐名计算岗位匹配评分',
    countNoun: '评分实例',
    candidateLevel: true,
  },
  {
    name: 'decision_review',
    title: '决策审查 Agent',
    subtitle: '逐名检查评分与风险',
    countNoun: '审查实例',
    candidateLevel: true,
  },
  {
    name: 'hr_report',
    title: 'HR 最终报告',
    subtitle: '汇总候选人排序与建议',
    countNoun: '报告生成实例',
    candidateLevel: false,
  },
  {
    name: 'interview_evaluation',
    title: '面试评估 Agent',
    subtitle: '',
    countNoun: '',
    candidateLevel: false,
  },
];

const definitionMap = new Map(definitions.map((definition) => [definition.name, definition]));
const workflowStages: WorkflowStage[] = [
  {
    key: 'strategy',
    groupLabel: null,
    nodes: [definitionMap.get('recruitment_strategy')!],
  },
  {
    key: 'analysis',
    groupLabel: '解析与匹配',
    nodes: [definitionMap.get('resume_parser')!, definitionMap.get('job_match')!],
  },
  {
    key: 'decision',
    groupLabel: '决策与报告',
    nodes: [definitionMap.get('decision_review')!, definitionMap.get('hr_report')!],
  },
  {
    key: 'interview',
    groupLabel: null,
    nodes: [definitionMap.get('interview_evaluation')!],
  },
];
const strategySubtitle = computed(() => {
  const total = props.snapshot?.total_candidates ?? props.snapshot?.candidate_ids.length ?? 0;
  return total > 0 ? `规划 ${total} 名候选人的评估流程` : definitionMap.get('recruitment_strategy')!.subtitle;
});

const CheckIcon = defineComponent({
  render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.5' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M5 13l4 4L19 7' }),
  ]),
});
const RunningIcon = defineComponent({
  render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.5' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 3v3m0 12v3M3 12h3m12 0h3M5.64 5.64l2.12 2.12m8.48 8.48 2.12 2.12m0-12.72-2.12 2.12M7.76 16.24l-2.12 2.12' }),
  ]),
});
const AlertIcon = defineComponent({
  render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.5' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 9v2m0 4h.01m-6.94 4h13.88L12 4 5.06 19z' }),
  ]),
});
const SkipIcon = defineComponent({
  render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.5' }, [
    h('path', { 'stroke-linecap': 'round', d: 'M6 12h12' }),
  ]),
});
const WaitingIcon = defineComponent({
  render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.2' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M7 3h8l4 4v14H7zM15 3v5h5M10 13h6m-6 4h6' }),
  ]),
});

function rawNodeStatus(nodeName: string): AgentNodeStatus {
  return props.snapshot?.nodes[nodeName] ?? AgentNodeStatus.WAITING;
}

function nodeStatus(nodeName: string): AgentNodeStatus {
  const snapshot = props.snapshot;
  const status = rawNodeStatus(nodeName);
  if (!snapshot || status !== AgentNodeStatus.WAITING || !hasNodeActivity(snapshot, nodeName)) return status;

  const lifecycleEvent = [...snapshot.events].reverse().find((event) =>
    event.node_name === nodeName && (
      event.event_type === AgentEventType.AGENT_STARTED
      || event.event_type === AgentEventType.AGENT_COMPLETED
    ),
  );
  return lifecycleEvent?.event_type === AgentEventType.AGENT_COMPLETED
    ? lifecycleEvent.status
    : AgentNodeStatus.RUNNING;
}

function shouldExpandNode(nodeName: string): boolean {
  const status = nodeStatus(nodeName);
  if (status === AgentNodeStatus.WAITING || status === AgentNodeStatus.SKIPPED) return false;
  return status === AgentNodeStatus.RUNNING
    || status === AgentNodeStatus.COMPLETED
    || status === AgentNodeStatus.NEEDS_REVIEW
    || status === AgentNodeStatus.FAILED
    || Boolean(props.snapshot && hasNodeActivity(props.snapshot, nodeName));
}

function isNodeExpanded(nodeName: string): boolean {
  return nodeName !== 'interview_evaluation' && shouldExpandNode(nodeName);
}

function nodeInstances(nodeName: string): AgentTaskInstance[] {
  const snapshot = props.snapshot;
  const definition = definitionMap.get(nodeName);
  if (!snapshot || !definition || nodeName === 'interview_evaluation') return [];
  if (definition.candidateLevel) {
    return buildCandidateTaskInstances(snapshot, nodeName, props.candidateNames);
  }
  return [buildSingletonTaskInstance(
    snapshot,
    nodeName as 'recruitment_strategy' | 'hr_report',
    nodeName === 'recruitment_strategy' ? '招聘策略规划' : '招聘评估报告',
  )];
}

function instanceCountLabel(nodeName: string): string {
  const definition = definitionMap.get(nodeName);
  if (!definition) return '';
  const count = definition.candidateLevel ? nodeInstances(nodeName).length : 1;
  return `${count} 个${definition.countNoun}`;
}

function nodeStatusLabel(status: AgentNodeStatus): string {
  return {
    [AgentNodeStatus.WAITING]: '等待执行',
    [AgentNodeStatus.RUNNING]: '运行中',
    [AgentNodeStatus.COMPLETED]: '已完成',
    [AgentNodeStatus.NEEDS_REVIEW]: '需要复核',
    [AgentNodeStatus.FAILED]: '失败',
    [AgentNodeStatus.SKIPPED]: '已跳过',
  }[status];
}

function nodeIcon(status: AgentNodeStatus) {
  switch (status) {
    case AgentNodeStatus.COMPLETED:
      return CheckIcon;
    case AgentNodeStatus.RUNNING:
      return RunningIcon;
    case AgentNodeStatus.NEEDS_REVIEW:
    case AgentNodeStatus.FAILED:
      return AlertIcon;
    case AgentNodeStatus.SKIPPED:
      return SkipIcon;
    default:
      return WaitingIcon;
  }
}

function stageConnectorClass(previousStage: WorkflowStage, nextStage: WorkflowStage): string {
  const previousPassed = previousStage.nodes.every((node) => isPassed(nodeStatus(node.name)));
  const nextPassed = nextStage.nodes.every((node) => isPassed(nodeStatus(node.name)));
  const nextRunning = nextStage.nodes.some((node) => nodeStatus(node.name) === AgentNodeStatus.RUNNING);
  if (previousPassed && nextRunning) return 'workflow-connector--active';
  if (previousPassed && nextPassed) return 'workflow-connector--completed';
  return 'workflow-connector--waiting';
}

function isPassed(status: AgentNodeStatus): boolean {
  return status === AgentNodeStatus.COMPLETED || status === AgentNodeStatus.SKIPPED;
}
</script>

<style scoped>
.workflow-board__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.workflow-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
  color: #94a3b8;
  font-size: 11px;
  font-weight: 700;
}

.workflow-legend span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.legend-dot--completed { background: #10b981; }
.legend-dot--running { background: #3b82f6; }
.legend-dot--review { background: #f59e0b; }

.workflow-canvas {
  width: 100%;
  overflow-x: auto;
  padding: 36px 24px 28px;
  border-radius: 16px;
  background: rgba(248, 250, 252, 0.55);
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.workflow-track {
  display: flex;
  align-items: center;
  width: max-content;
  min-width: 100%;
}

.workflow-stage {
  position: relative;
  flex: 0 0 auto;
}

.workflow-stage--single {
  display: flex;
  align-items: center;
}

.workflow-stage--group {
  padding: 25px 14px 14px;
  border: 1px dashed #cbd5e1;
  border-radius: 22px;
  background: rgba(248, 250, 252, 0.68);
}

.workflow-stage__label {
  position: absolute;
  top: -11px;
  left: 16px;
  padding: 3px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

.workflow-stage__nodes {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.workflow-node {
  flex: 0 0 auto;
  min-height: 112px;
  border-radius: 16px;
  text-align: left;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.07);
  cursor: pointer;
  transition: width 220ms ease, max-height 220ms ease, border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}

.workflow-node:focus-visible {
  outline: 3px solid rgba(59, 130, 246, 0.35);
  outline-offset: 3px;
}

.workflow-node--compact {
  display: flex;
  flex-direction: column;
  width: 172px;
  max-height: 146px;
  padding: 20px 14px;
  align-items: center;
  justify-content: center;
}

.workflow-node--expanded {
  width: 268px;
  max-height: 1200px;
  padding: 16px;
}

.workflow-node--selected {
  box-shadow: 0 0 0 2px #3b82f6, 0 0 0 5px rgba(59, 130, 246, 0.12);
}

.workflow-node--waiting {
  border: 1px dashed #cbd5e1;
  background: #f8fafc;
}

.workflow-node--running { border: 1px solid #60a5fa; background: #fff; }
.workflow-node--completed { border: 1px solid #dbe4ef; background: #fff; }
.workflow-node--needs_review { border: 1px solid #fcd34d; background: #fff; }
.workflow-node--failed { border: 1px solid #fca5a5; background: #fff; }
.workflow-node--skipped { border: 1px solid #dbe4ef; background: rgba(248, 250, 252, 0.75); }

.workflow-node__main {
  display: flex;
  align-items: center;
  gap: 10px;
}

.workflow-node--compact .workflow-node__main {
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.workflow-node__icon {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 999px;
  background: #fff;
  color: #94a3b8;
  box-shadow: inset 0 0 0 1px #e2e8f0;
}

.workflow-node__icon :deep(svg) { width: 18px; height: 18px; }
.workflow-node--running .workflow-node__icon { background: #dbeafe; color: #2563eb; box-shadow: none; }
.workflow-node--completed .workflow-node__icon { background: #ecfdf5; color: #059669; box-shadow: none; }
.workflow-node--needs_review .workflow-node__icon { background: #fffbeb; color: #d97706; box-shadow: none; }
.workflow-node--failed .workflow-node__icon { background: #fef2f2; color: #dc2626; box-shadow: none; }

.workflow-node__heading {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
}

.workflow-node__heading strong {
  color: #334155;
  font-size: 13px;
  line-height: 1.35;
}

.node-status {
  margin-top: 3px;
  color: #94a3b8;
  font-size: 10px;
  font-weight: 700;
}

.node-status--running { color: #2563eb; }
.node-status--completed { color: #059669; }
.node-status--needs_review { color: #d97706; }
.node-status--failed { color: #dc2626; }

.workflow-node__details {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.workflow-node__subtitle,
.workflow-node__skip-reason {
  color: #64748b;
  font-size: 11px;
  line-height: 1.5;
}

.workflow-node__subtitle { margin-bottom: 8px; }
.workflow-node__skip-reason { margin-top: 8px; text-align: center; }

.workflow-node__count {
  margin-top: 10px;
  padding-top: 9px;
  border-top: 1px solid #f1f5f9;
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
}

.node-details-enter-active,
.node-details-leave-active {
  transition: max-height 220ms ease, opacity 180ms ease, transform 180ms ease;
  overflow: hidden;
}

.node-details-enter-from,
.node-details-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-4px);
}

.node-details-enter-to,
.node-details-leave-from {
  max-height: 900px;
  opacity: 1;
  transform: translateY(0);
}

.workflow-connector {
  position: relative;
  flex: 0 0 42px;
  height: 112px;
  overflow: hidden;
}

.workflow-connector__line {
  position: absolute;
  top: 55px;
  left: 7px;
  width: 29px;
  height: 2px;
  background: #cbd5e1;
}

.workflow-connector__arrow {
  position: absolute;
  top: 51px;
  right: 5px;
  width: 0;
  height: 0;
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
  border-left: 7px solid #cbd5e1;
}

.workflow-connector--completed .workflow-connector__line { background: #10b981; }
.workflow-connector--completed .workflow-connector__arrow { border-left-color: #10b981; }
.workflow-connector--active .workflow-connector__line { background: #3b82f6; }
.workflow-connector--active .workflow-connector__arrow { border-left-color: #3b82f6; }

.workflow-connector--active .workflow-connector__line::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.9), transparent);
  transform: translateX(-100%);
  animation: connectorFlow 900ms ease-out 1;
}

@keyframes connectorFlow {
  to { transform: translateX(100%); }
}

[data-theme="dark"] .workflow-board { background: #1e293c !important; border-color: #334155 !important; }
[data-theme="dark"] .workflow-board__header { border-color: #334155 !important; }
[data-theme="dark"] .workflow-canvas { background: rgba(15, 23, 42, 0.5); }
[data-theme="dark"] .workflow-stage--group { background: rgba(15, 23, 42, 0.34); border-color: #475569; }
[data-theme="dark"] .workflow-stage__label { background: #1e293b; border-color: #475569; color: #94a3b8; }
[data-theme="dark"] .workflow-node--waiting,
[data-theme="dark"] .workflow-node--skipped { background: #172033; border-color: #475569; }
[data-theme="dark"] .workflow-node--running,
[data-theme="dark"] .workflow-node--completed,
[data-theme="dark"] .workflow-node--needs_review,
[data-theme="dark"] .workflow-node--failed { background: #1e293b; }
[data-theme="dark"] .workflow-node__heading strong { color: #e2e8f0; }
[data-theme="dark"] .workflow-node__details,
[data-theme="dark"] .workflow-node__count { border-color: #334155; }
[data-theme="dark"] .workflow-node__subtitle,
[data-theme="dark"] .workflow-node__skip-reason,
[data-theme="dark"] .workflow-node__count { color: #94a3b8; }
[data-theme="dark"] .workflow-node__icon { background: #1e293b; box-shadow: inset 0 0 0 1px #475569; }

@media (max-width: 720px) {
  .workflow-board { padding: 20px; }
  .workflow-board__header { flex-direction: column; }
  .workflow-legend { justify-content: flex-start; }
  .workflow-canvas { padding-inline: 16px; }
}
</style>
