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
import { AgentNodeStatus, type AgentEvent, type RecruitmentRunSnapshot } from '../../../../shared/agent/contracts';

const props = defineProps<{ snapshot: RecruitmentRunSnapshot | null; selectedNode?: string }>();
const emit = defineEmits<{ select: [nodeName: string] }>();
interface NodeView { name:string; label:string; status:AgentNodeStatus; action:string; duration:number|null; eventCount:number; skipReason:string; selected:boolean; }
const definitions = [
  ['recruitment_strategy','招聘策略 Agent'],['resume_parser','简历解析 Agent'],['job_match','岗位匹配 Agent'],
  ['interview_evaluation','面试评估 Agent'],['decision_review','决策审查 Agent'],['hr_report','HR 最终报告'],
] as const;
const nodeMap = computed<Record<string, NodeView>>(() => Object.fromEntries(definitions.map(([name,label]) => [name, buildNode(name,label)])));

function buildNode(name:string,label:string):NodeView {
  const nodeEvents = (props.snapshot?.events || []).filter((event) => event.node_name === name);
  const last = nodeEvents[nodeEvents.length - 1];
  return {
    name,label,status:props.snapshot?.nodes[name] || AgentNodeStatus.WAITING,
    action:readAction(last),duration:last?.duration_ms ?? null,eventCount:nodeEvents.length,
    skipReason:(props.snapshot?.nodes[name] === AgentNodeStatus.SKIPPED) ? '后续阶段接入 · CURRENT_PHASE_NOT_IMPLEMENTED' : '',
    selected:props.selectedNode === name,
  };
}
function readAction(event:AgentEvent|undefined):string {
  const value=event?.summary.current_action;
  return typeof value === 'string' ? value : event?.display_name || '等待真实运行事件';
}
const NodeCard = defineComponent({
  props:{ node:{ type:Object as PropType<NodeView>, required:true } },
  setup(componentProps){ return()=>h('button',{class:['node-card',`node-card--${componentProps.node.status.toLowerCase()}`,{'node-card--selected':componentProps.node.selected}],onClick:()=>emit('select',componentProps.node.name)},[
    h('div',{class:'node-card__head'},[h('strong',componentProps.node.label),h('span',componentProps.node.status)]),
    h('p',componentProps.node.skipReason || componentProps.node.action),
    h('small',`事件 ${componentProps.node.eventCount} · 耗时 ${componentProps.node.duration === null ? '—' : `${componentProps.node.duration} ms`}`),
  ]); },
});
</script>

<style scoped>
.workflow-board { display:grid; align-content:start; justify-items:center; padding:22px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:#fff; box-shadow:var(--shadow-card); }.workflow-board header { display:flex; width:100%; align-items:flex-end; justify-content:space-between; margin-bottom:18px; }.workflow-board header span { color:var(--color-primary); font-size:12px; font-weight:800; }.workflow-board h2 { margin:5px 0 0; }.workflow-board header>strong { color:var(--color-muted); font-size:12px; }.goal-node { padding:12px 20px; border-radius:var(--radius-sm); background:var(--color-primary-soft); color:var(--color-primary); font-weight:900; }.connector { color:var(--color-subtle); font-weight:900; line-height:28px; }.professional-nodes { display:grid; width:100%; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }
:deep(.node-card) { width:min(100%,360px); padding:14px; border:1px solid var(--color-line); border-radius:var(--radius-sm); background:#f8fafc; color:var(--color-text); text-align:left; }:deep(.professional-nodes .node-card) { width:100%; }:deep(.node-card__head) { display:flex; justify-content:space-between; gap:8px; }:deep(.node-card__head span) { color:var(--color-muted); font-size:11px; font-weight:900; }:deep(.node-card p) { min-height:38px; margin:10px 0; color:var(--color-muted); font-size:12px; line-height:1.5; }:deep(.node-card small) { color:var(--color-subtle); }
:deep(.node-card--running) { border-color:var(--color-primary); box-shadow:0 0 0 3px rgba(36,85,245,.1); animation:runningPulse 1.4s ease-in-out infinite; }:deep(.node-card--completed) { border-color:#86efac; background:#f0fdf4; }:deep(.node-card--skipped) { border-color:#fde68a; background:#fffbeb; }:deep(.node-card--failed) { border-color:#fecaca; background:#fff7f7; }:deep(.node-card--needs_review) { border-color:#fdba74; background:#fff7ed; }:deep(.node-card--selected) { outline:2px solid rgba(36,85,245,.22); }
@keyframes runningPulse { 50% { box-shadow:0 0 0 5px rgba(36,85,245,.06); } } @media(max-width:850px){.professional-nodes{grid-template-columns:1fr;}}
</style>

