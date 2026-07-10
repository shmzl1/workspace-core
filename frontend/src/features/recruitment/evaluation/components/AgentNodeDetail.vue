<template>
  <section class="node-detail">
    <header><div><span>运行详情</span><h2>{{ metadata.label }}</h2></div><strong>{{ nodeStatus }}</strong></header>
    <dl v-if="snapshot" class="node-detail__ids">
      <div><dt>run_id</dt><dd>{{ snapshot.run_id }}</dd></div><div><dt>trace_id</dt><dd>{{ snapshot.trace_id }}</dd></div>
      <div><dt>节点事件</dt><dd>{{ nodeEvents.length }}</dd></div><div><dt>回退状态</dt><dd>{{ fallbackUsed ? '已使用' : '未使用' }}</dd></div>
    </dl>
    <div class="node-detail__grid">
      <article><h3>Agent 任务</h3><p>{{ metadata.task }}</p></article>
      <article><h3>输入摘要</h3><pre>{{ inputSummary }}</pre></article>
      <article><h3>当前动作</h3><p>{{ currentAction }}</p></article>
      <article><h3>Tool 调用</h3><p>{{ toolSummary }}</p></article>
      <article><h3>检索来源</h3><p>{{ sourceSummary }}</p></article>
      <article><h3>结构化中间结果</h3><pre>{{ intermediateSummary }}</pre></article>
      <article><h3>最终结论</h3><pre>{{ finalSummary }}</pre></article>
      <article><h3>错误定位</h3><p>{{ errorSummary }}</p></article>
    </div>
    <div v-if="strategyPlan" class="node-detail__plan">
      <h3>招聘策略执行计划</h3>
      <p><b>required_nodes</b>{{ strategyPlan.required_nodes.join(' → ') }}</p>
      <p><b>executed_nodes</b>{{ strategyPlan.executed_nodes.join('、') }}</p>
      <p><b>skipped_nodes</b>{{ strategyPlan.skipped_nodes.join('、') }}</p>
      <ul><li v-for="note in strategyPlan.plan_notes" :key="note">{{ note }}</li></ul>
    </div>
    <div v-else-if="nodeStatus === AgentNodeStatus.SKIPPED" class="node-detail__empty">
      当前节点因 CURRENT_PHASE_NOT_IMPLEMENTED 未执行，不展示策略节点结果作为本节点结果。
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import {
  AgentEventType,
  AgentNodeStatus,
  type AgentEvent,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';

const props=defineProps<{ snapshot:RecruitmentRunSnapshot|null; nodeName:string }>();
const definitions:Record<string,{label:string;task:string}>={
  recruitment_strategy:{label:'招聘策略 Agent',task:'读取已校验招聘目标与工作流元数据，生成当前阶段结构化执行计划。'},
  resume_parser:{label:'简历解析 Agent',task:'计划从真实候选人材料提取事实与证据；Sprint 2.1 不执行。'},
  job_match:{label:'岗位匹配 Agent',task:'计划经 Tool 调用 Service 汇总确定性评分；Sprint 2.1 不执行。'},
  interview_evaluation:{label:'面试评估 Agent',task:'仅使用真实结构化面试数据；Sprint 2.1 不执行。'},
  decision_review:{label:'决策审查 Agent',task:'计划检查证据、来源和节点分歧；Sprint 2.1 不执行。'},
  hr_report:{label:'HR 最终报告',task:'计划汇总可审计建议并交由 HR 决策；Sprint 2.1 不执行。'},
};
const metadata=computed(()=>definitions[props.nodeName]||{label:'节点详情',task:'未知节点'});
const nodeStatus=computed(()=>props.snapshot?.nodes[props.nodeName]||AgentNodeStatus.WAITING);
const nodeEvents=computed(()=>props.snapshot?.events.filter((event)=>event.node_name===props.nodeName)||[]);
const strategyPlan=computed(()=>props.nodeName==='recruitment_strategy' ? props.snapshot?.execution_plan||null : null);
const fallbackUsed=computed(()=>nodeEvents.value.some((event)=>event.fallback_used));
const inputSummary=computed(()=>formatSummary(findEvent([
  AgentEventType.AGENT_THINKING,AgentEventType.AGENT_STARTED,
])?.summary,'等待真实节点输入事件'));
const currentAction=computed(()=>{
  const event=[...nodeEvents.value].reverse().find((item)=>typeof item.summary.current_action==='string');
  return typeof event?.summary.current_action==='string' ? event.summary.current_action : nodeStatus.value===AgentNodeStatus.SKIPPED ? '当前阶段未执行' : '等待真实运行事件';
});
const toolSummary=computed(()=>{
  const tools=nodeEvents.value.map((event)=>event.tool_name).filter((name):name is string=>Boolean(name));
  return tools.length ? [...new Set(tools)].join('、') : '本阶段未调用';
});
const sourceSummary=computed(()=>{
  const count=nodeEvents.value.reduce((max,event)=>Math.max(max,event.source_count),0);
  if(!count) return '本阶段未检索';
  return props.snapshot?.sources.map((source)=>`${source.title}（${source.source_id}）`).join('、')||`已检索 ${count} 个来源`;
});
const intermediateSummary=computed(()=>formatSummary(findEvent([AgentEventType.INTERMEDIATE_RESULT])?.summary,'本阶段无中间结果'));
const finalSummary=computed(()=>formatSummary(findEvent([
  AgentEventType.AGENT_COMPLETED,AgentEventType.REVIEW_COMPLETED,AgentEventType.REPORT_GENERATED,
])?.summary,nodeStatus.value===AgentNodeStatus.SKIPPED?'当前阶段未执行':'尚无真实最终结论'));
const errorSummary=computed(()=>{
  const event=[...nodeEvents.value].reverse().find((item)=>item.error);
  const error=event?.error;
  if(!error) return '无错误';
  const failedNode=safeDetail(error.details.failed_node);
  const failedStep=safeDetail(error.details.failed_step);
  return `${error.code}：${error.message}；节点：${failedNode||event?.node_name||'未知'}；步骤：${failedStep||'未知'}`;
});

function findEvent(types:AgentEventType[]):AgentEvent|undefined {
  return [...nodeEvents.value].reverse().find((event)=>types.includes(event.event_type));
}
function formatSummary(summary:Record<string,unknown>|undefined,empty:string):string {
  return summary ? JSON.stringify(summary,null,2) : empty;
}
function safeDetail(value:unknown):string { return typeof value==='string' ? value : ''; }
</script>

<style scoped>
.node-detail { display:grid; gap:16px; padding:22px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:#fff; box-shadow:var(--shadow-card); }.node-detail header { display:flex; align-items:flex-end; justify-content:space-between; }.node-detail header span { color:var(--color-primary); font-size:12px; font-weight:800; }.node-detail h2 { margin:5px 0 0; }.node-detail header strong { color:var(--color-muted); }.node-detail__ids { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:0; }.node-detail__ids div { min-width:0; padding:11px; border-radius:10px; background:var(--color-surface-soft); }.node-detail dt { color:var(--color-subtle); font-size:11px; }.node-detail dd { overflow:hidden; margin:5px 0 0; color:var(--color-text); font-size:12px; font-weight:800; text-overflow:ellipsis; }.node-detail__grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }.node-detail article,.node-detail__plan { min-width:0; padding:14px; border:1px solid var(--color-line); border-radius:12px; }.node-detail article h3,.node-detail__plan h3 { margin:0 0 10px; font-size:13px; }.node-detail article p { margin:0; color:var(--color-muted); font-size:12px; line-height:1.6; }.node-detail article pre { overflow:auto; max-height:180px; margin:0; color:#334155; font:11px/1.5 ui-monospace,monospace; white-space:pre-wrap; }.node-detail__plan p { display:grid; grid-template-columns:130px 1fr; margin:7px 0; color:var(--color-muted); font-size:13px; }.node-detail__plan b { color:var(--color-text); }.node-detail__plan ul { margin:12px 0 0; color:var(--color-muted); }.node-detail__empty { color:var(--color-muted); }
@media(max-width:850px){.node-detail__ids,.node-detail__grid{grid-template-columns:1fr 1fr}} @media(max-width:560px){.node-detail__ids,.node-detail__grid{grid-template-columns:1fr}.node-detail__plan p{grid-template-columns:1fr}}
</style>
