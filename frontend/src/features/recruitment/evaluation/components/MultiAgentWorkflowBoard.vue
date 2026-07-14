<template>
  <section class="workflow-board">
    <button type="button" class="workflow-board__toggle" @click="collapsed = !collapsed">
      <div class="workflow-board__heading">
        <span>顶层工作流</span>
        <h2>招聘多 Agent 流程</h2>
      </div>
      <div class="workflow-board__meta">
        <strong>{{ snapshot?.status || 'WAITING' }}</strong>
        <svg class="workflow-board__chevron" :class="{ 'workflow-board__chevron--collapsed': collapsed }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
      </div>
    </button>
    <div v-if="!collapsed" class="workflow-board__body">
      <div class="goal-node">企业招聘目标</div>
      <div class="connector">↓</div>
      <NodeCard :node="nodeMap.recruitment_strategy" :collapsed="!expandedNodes.has('recruitment_strategy')" @toggle="toggleNode('recruitment_strategy')" />
      <div class="connector">↓</div>
      <div class="professional-nodes">
        <NodeCard v-for="name in ['resume_parser','job_match','interview_evaluation']" :key="name" :node="nodeMap[name]" :collapsed="!expandedNodes.has(name)" @toggle="toggleNode(name)" />
      </div>
      <div class="connector">↓</div>
      <NodeCard :node="nodeMap.decision_review" :collapsed="!expandedNodes.has('decision_review')" @toggle="toggleNode('decision_review')" />
      <div class="connector">↓</div>
      <NodeCard :node="nodeMap.hr_report" :collapsed="!expandedNodes.has('hr_report')" @toggle="toggleNode('hr_report')" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, reactive, ref, type PropType } from 'vue';
import {
  AgentEventType,
  AgentNodeStatus,
  type AgentEvent,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';

const props = defineProps<{ snapshot: RecruitmentRunSnapshot | null; selectedNode?: string }>();
const emit = defineEmits<{ select: [nodeName: string] }>();
const collapsed = ref(false);
const expandedNodes = reactive(new Set<string>());

function toggleNode(name: string): void {
  if (expandedNodes.has(name)) {
    expandedNodes.delete(name);
  } else {
    expandedNodes.add(name);
  }
}

interface NodeView {
  name: string; label: string; status: AgentNodeStatus; action: string; duration: number | null;
  eventCount: number; skipReason: string; selected: boolean; tool: string; sourceCount: number; output: string;
}
const definitions = [
  ['recruitment_strategy', '招聘策略 Agent'], ['resume_parser', '简历解析 Agent'], ['job_match', '岗位匹配 Agent'],
  ['interview_evaluation', '面试评估 Agent'], ['decision_review', '决策审查 Agent'], ['hr_report', 'HR 最终报告'],
] as const;
const nodeMap = computed<Record<string, NodeView>>(() => Object.fromEntries(
  definitions.map(([name, label]) => [name, buildNode(name, label)]),
));

function buildNode(name: string, label: string): NodeView {
  const nodeEvents = (props.snapshot?.events || []).filter((event) => event.node_name === name);
  const actionEvent = findLast(nodeEvents, (event) => typeof event.summary.current_action === 'string');
  const toolEvent = findLast(nodeEvents, (event) => Boolean(event.tool_name));
  const durationEvent = findLast(nodeEvents, (event) => event.duration_ms !== null);
  const outputEvent = findLast(nodeEvents, (event) => [
    AgentEventType.INTERMEDIATE_RESULT, AgentEventType.AGENT_COMPLETED,
    AgentEventType.REVIEW_COMPLETED, AgentEventType.REPORT_GENERATED,
  ].includes(event.event_type));
  const status = props.snapshot?.nodes[name] || AgentNodeStatus.WAITING;
  const skipReason = status === AgentNodeStatus.SKIPPED ? resolveSkipReason(name, nodeEvents) : '';
  return {
    name, label, status,
    action: typeof actionEvent?.summary.current_action === 'string'
      ? actionEvent.summary.current_action : nodeEvents.at(-1)?.display_name || '等待真实运行事件',
    duration: durationEvent?.duration_ms ?? null,
    eventCount: nodeEvents.length,
    skipReason,
    selected: props.selectedNode === name,
    tool: toolEvent?.tool_name || '本阶段未调用',
    sourceCount: nodeEvents.reduce((max, event) => Math.max(max, event.source_count), 0),
    output: status === AgentNodeStatus.SKIPPED
      ? outputEvent ? summarize(outputEvent.summary) : skippedOutput(name)
      : summarize(outputEvent?.summary),
  };
}
function findLast(events: AgentEvent[], predicate: (event: AgentEvent) => boolean): AgentEvent | undefined {
  return [...events].reverse().find(predicate);
}
function summarize(summary: Record<string, unknown> | undefined): string {
  if (!summary) return '尚无真实结果摘要';
  const preferred = summary.current_conclusion ?? summary.output_summary ?? summary.completed_node;
  if (typeof preferred === 'string') return preferred;
  const text = JSON.stringify(summary);
  return text.length > 100 ? `${text.slice(0, 97)}…` : text;
}
function resolveSkipReason(name: string, events: AgentEvent[]): string {
  const event = [...events].reverse().find((item) => item.status === AgentNodeStatus.SKIPPED);
  const directReason = event?.summary.skip_reason ?? event?.summary.reason;
  if (typeof directReason === 'string') return directReason;
  const reasons = event?.summary.skip_reasons;
  if (reasons && typeof reasons === 'object') {
    const nodeReason = (reasons as Record<string, unknown>)[name];
    if (typeof nodeReason === 'string') return nodeReason;
  }
  return name === 'interview_evaluation' ? 'STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE' : '节点已由后端标记为跳过';
}
function skippedOutput(name: string): string {
  return name === 'interview_evaluation'
    ? '未生成面试评分或结论，决策审查将标记缺少真实面试评价。'
    : '节点未产生结构化结果。';
}

const NodeCard = defineComponent({
  props: {
    node: { type: Object as PropType<NodeView>, required: true },
    collapsed: { type: Boolean, default: true },
  },
  emits: ['toggle'],
  setup(componentProps, { emit: cardEmit }) {
    return () => h('div', { class: ['node-card', `node-card--${componentProps.node.status.toLowerCase()}`, { 'node-card--selected': componentProps.node.selected }] }, [
      h('button', {
        type: 'button',
        class: 'node-card__toggle',
        onClick: (e: Event) => {
          e.stopPropagation();
          cardEmit('toggle');
        },
      }, [
        h('div', { class: 'node-card__head' }, [
          h('strong', componentProps.node.label),
          h('span', componentProps.node.status),
        ]),
        h('p', componentProps.node.skipReason || componentProps.node.action),
        h('svg', {
          class: ['node-card__chevron', { 'node-card__chevron--collapsed': componentProps.collapsed }],
          width: '14', height: '14', viewBox: '0 0 24 24', fill: 'none',
          stroke: 'currentColor', 'stroke-width': '2.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round',
        }, [h('polyline', { points: '6 9 12 15 18 9' })]),
      ]),
      componentProps.collapsed ? null : h('div', { class: 'node-card__detail' }, [
        h('dl', { class: 'node-card__meta' }, [
          h('div', [h('dt', '最近 Tool'), h('dd', componentProps.node.tool)]),
          h('div', [h('dt', '知识来源'), h('dd', `${componentProps.node.sourceCount}`)]),
          h('div', [h('dt', '结果摘要'), h('dd', componentProps.node.output)]),
        ]),
        h('small', `事件 ${componentProps.node.eventCount} · 耗时 ${componentProps.node.duration === null ? '—' : `${componentProps.node.duration} ms`}`),
      ]),
    ]);
  },
});
</script>

<style scoped>
.workflow-board {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}
.workflow-board__toggle {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  padding: 22px;
  border: none;
  background: none;
  color: inherit;
  cursor: pointer;
}
.workflow-board__heading span {
  display: block;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 800;
  text-align: left;
}
.workflow-board__heading h2 {
  margin: 5px 0 0;
  text-align: left;
}
.workflow-board__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.workflow-board__meta strong {
  color: var(--color-muted);
  font-size: 12px;
  white-space: nowrap;
}
.workflow-board__chevron {
  color: var(--color-subtle);
  transition: transform 0.25s ease;
}
.workflow-board__chevron--collapsed {
  transform: rotate(-90deg);
}
.workflow-board__body {
  display: grid;
  align-content: start;
  justify-items: center;
  padding: 0 22px 22px;
}
.goal-node {
  padding: 12px 20px;
  border-radius: var(--radius-sm);
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-weight: 900;
}
.connector {
  color: var(--color-subtle);
  font-weight: 900;
  line-height: 28px;
}
.professional-nodes {
  display: grid;
  width: 100%;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
:deep(.node-card) {
  width: min(100%, 420px);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: var(--color-surface-soft);
  color: var(--color-text);
}
:deep(.professional-nodes .node-card) { width: 100%; }
:deep(.node-card__toggle) {
  position: relative;
  display: grid;
  width: 100%;
  padding: 14px 30px 14px 14px;
  border: none;
  background: none;
  color: inherit;
  cursor: pointer;
  text-align: left;
}
:deep(.node-card__head) {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}
:deep(.node-card__head span) {
  color: var(--color-muted);
  font-size: 11px;
  font-weight: 900;
}
:deep(.node-card__toggle > p) {
  min-height: 20px;
  margin: 8px 0 0;
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.5;
}
:deep(.node-card__chevron) {
  position: absolute;
  top: 14px;
  right: 14px;
  color: var(--color-subtle);
  transition: transform 0.25s ease;
}
:deep(.node-card__chevron--collapsed) {
  transform: rotate(-90deg);
}
:deep(.node-card__detail) {
  padding: 0 14px 14px;
}
:deep(.node-card__meta) {
  display: grid;
  gap: 6px;
  margin: 0;
}
:deep(.node-card__meta div) {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 6px;
}
:deep(.node-card__meta dt) {
  color: var(--color-subtle);
  font-size: 10px;
}
:deep(.node-card__meta dd) {
  overflow: hidden;
  margin: 0;
  color: var(--color-muted);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
:deep(.node-card small) {
  display: block;
  margin-top: 8px;
  color: var(--color-subtle);
}
:deep(.node-card--running) {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-node-running-glow);
  animation: runningPulse 1.4s ease-in-out infinite;
}
:deep(.node-card--completed) {
  border-color: var(--color-node-completed-border);
  background: var(--color-node-completed-bg);
}
:deep(.node-card--skipped) {
  border-color: var(--color-node-skipped-border);
  background: var(--color-node-skipped-bg);
}
:deep(.node-card--failed) {
  border-color: var(--color-node-failed-border);
  background: var(--color-node-failed-bg);
}
:deep(.node-card--needs_review) {
  border-color: var(--color-node-review-border);
  background: var(--color-node-review-bg);
}
:deep(.node-card--selected) {
  outline: 2px solid var(--color-node-selected-outline);
}
@keyframes runningPulse {
  50% { box-shadow: 0 0 0 5px var(--color-node-running-glow); }
}
@media (max-width: 850px) {
  .professional-nodes { grid-template-columns: 1fr; }
}
</style>
