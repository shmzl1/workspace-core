<template>
  <section class="workflow-board">
    <header><div><span>顶层工作流</span><h2>招聘多 Agent 流程</h2></div><strong>{{ snapshot?.status || 'WAITING' }}</strong></header>
    <div class="goal-node">企业招聘目标</div><div class="connector">↓</div>
    <NodeCard :node="nodeMap.recruitment_strategy" />
    <div class="connector">↓</div>
    <div class="professional-nodes">
      <NodeCard :node="nodeMap.resume_parser" /><NodeCard :node="nodeMap.job_match" /><NodeCard :node="nodeMap.interview_evaluation" />
    </div>
    <div class="connector">↓</div><NodeCard :node="nodeMap.decision_review" />
    <div class="connector">↓</div><NodeCard :node="nodeMap.hr_report" />
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, type PropType } from 'vue';
import {
  AgentEventType,
  AgentNodeStatus,
  type AgentEvent,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';

const props = defineProps<{ snapshot: RecruitmentRunSnapshot | null; selectedNode?: string }>();
const emit = defineEmits<{ select: [nodeName: string] }>();
interface NodeView {
  name:string; label:string; status:AgentNodeStatus; action:string; duration:number|null;
  eventCount:number; skipReason:string; selected:boolean; tool:string; sourceCount:number; output:string;
}
const definitions = [
  ['recruitment_strategy','招聘策略 Agent'],['resume_parser','简历解析 Agent'],['job_match','岗位匹配 Agent'],
  ['interview_evaluation','面试评估 Agent'],['decision_review','决策审查 Agent'],['hr_report','HR 最终报告'],
] as const;
const nodeMap = computed<Record<string, NodeView>>(() => Object.fromEntries(
  definitions.map(([name,label]) => [name, buildNode(name,label)]),
));

function buildNode(name:string,label:string):NodeView {
  const nodeEvents = (props.snapshot?.events || []).filter((event) => event.node_name === name);
  const actionEvent = findLast(nodeEvents, (event) => typeof event.summary.current_action === 'string');
  const toolEvent = findLast(nodeEvents, (event) => Boolean(event.tool_name));
  const durationEvent = findLast(nodeEvents, (event) => event.duration_ms !== null);
  const outputEvent = findLast(nodeEvents, (event) => [
    AgentEventType.INTERMEDIATE_RESULT,
    AgentEventType.AGENT_COMPLETED,
    AgentEventType.REVIEW_COMPLETED,
    AgentEventType.REPORT_GENERATED,
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
function findLast(events:AgentEvent[], predicate:(event:AgentEvent)=>boolean):AgentEvent|undefined {
  return [...events].reverse().find(predicate);
}
function summarize(summary:Record<string,unknown>|undefined):string {
  if (!summary) return '尚无真实结果摘要';
  const preferred = summary.current_conclusion ?? summary.output_summary ?? summary.completed_node;
  if (typeof preferred === 'string') return preferred;
  const text = JSON.stringify(summary);
  return text.length > 100 ? `${text.slice(0,97)}…` : text;
}
function resolveSkipReason(name:string,events:AgentEvent[]):string {
  const event=[...events].reverse().find((item)=>item.status===AgentNodeStatus.SKIPPED);
  const directReason=event?.summary.skip_reason??event?.summary.reason;
  if(typeof directReason==='string') return directReason;
  const reasons=event?.summary.skip_reasons;
  if(reasons&&typeof reasons==='object') {
    const nodeReason=(reasons as Record<string,unknown>)[name];
    if(typeof nodeReason==='string') return nodeReason;
  }
  return name==='interview_evaluation'
    ? 'STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE'
    : '节点已由后端标记为跳过';
}
function skippedOutput(name:string):string {
  return name==='interview_evaluation'
    ? '未生成面试评分或结论，决策审查将标记缺少真实面试评价。'
    : '节点未产生结构化结果。';
}
const NodeCard = defineComponent({
  props:{ node:{ type:Object as PropType<NodeView>, required:true } },
  setup(componentProps){ return()=>h('button',{class:['node-card',`node-card--${componentProps.node.status.toLowerCase()}`,{'node-card--selected':componentProps.node.selected}],onClick:()=>emit('select',componentProps.node.name)},[
    h('div',{class:'node-card__head'},[h('strong',componentProps.node.label),h('span',componentProps.node.status)]),
    h('p',componentProps.node.skipReason || componentProps.node.action),
    h('dl',{class:'node-card__meta'},[
      h('div',[h('dt','最近 Tool'),h('dd',componentProps.node.tool)]),
      h('div',[h('dt','知识来源'),h('dd',`${componentProps.node.sourceCount}`)]),
      h('div',[h('dt','结果摘要'),h('dd',componentProps.node.output)]),
    ]),
    h('small',`事件 ${componentProps.node.eventCount} · 耗时 ${componentProps.node.duration === null ? '—' : `${componentProps.node.duration} ms`}`),
  ]); },
});
</script>

<style scoped>
.workflow-board { display:grid; align-content:start; justify-items:center; padding:22px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:#fff; box-shadow:var(--shadow-card); }.workflow-board header { display:flex; width:100%; align-items:flex-end; justify-content:space-between; margin-bottom:18px; }.workflow-board header span { color:var(--color-primary); font-size:12px; font-weight:800; }.workflow-board h2 { margin:5px 0 0; }.workflow-board header>strong { color:var(--color-muted); font-size:12px; }.goal-node { padding:12px 20px; border-radius:var(--radius-sm); background:var(--color-primary-soft); color:var(--color-primary); font-weight:900; }.connector { color:var(--color-subtle); font-weight:900; line-height:28px; }.professional-nodes { display:grid; width:100%; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }
:deep(.node-card) { width:min(100%,420px); padding:14px; border:1px solid var(--color-line); border-radius:var(--radius-sm); background:#f8fafc; color:var(--color-text); text-align:left; cursor:pointer; }:deep(.professional-nodes .node-card) { width:100%; }:deep(.node-card__head) { display:flex; justify-content:space-between; gap:8px; }:deep(.node-card__head span) { color:var(--color-muted); font-size:11px; font-weight:900; }:deep(.node-card p) { min-height:38px; margin:10px 0; color:var(--color-muted); font-size:12px; line-height:1.5; }:deep(.node-card small) { color:var(--color-subtle); }
:deep(.node-card__meta) { display:grid; gap:6px; margin:0 0 10px; }:deep(.node-card__meta div) { display:grid; grid-template-columns:72px 1fr; gap:6px; }:deep(.node-card__meta dt) { color:var(--color-subtle); font-size:10px; }:deep(.node-card__meta dd) { overflow:hidden; margin:0; color:var(--color-muted); font-size:11px; text-overflow:ellipsis; white-space:nowrap; }
:deep(.node-card--running) { border-color:var(--color-primary); box-shadow:0 0 0 3px rgba(36,85,245,.1); animation:runningPulse 1.4s ease-in-out infinite; }:deep(.node-card--completed) { border-color:#86efac; background:#f0fdf4; }:deep(.node-card--skipped) { border-color:#fde68a; background:#fffbeb; }:deep(.node-card--failed) { border-color:#fecaca; background:#fff7f7; }:deep(.node-card--needs_review) { border-color:#fdba74; background:#fff7ed; }:deep(.node-card--selected) { outline:2px solid rgba(36,85,245,.22); }
@keyframes runningPulse { 50% { box-shadow:0 0 0 5px rgba(36,85,245,.06); } } @media(max-width:850px){.professional-nodes{grid-template-columns:1fr;}}
</style>
