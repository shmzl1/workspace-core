<template>
  <section class="node-detail" :class="{ 'node-detail--collapsed': collapsed }">
    <button type="button" class="node-detail__toggle" @click="collapsed = !collapsed">
      <div><span>运行详情</span><h2>{{ metadata.label }}</h2></div>
      <div class="node-detail__toggle-meta">
        <strong>{{ nodeStatus }}</strong>
        <svg class="node-detail__chevron" :class="{ 'node-detail__chevron--collapsed': collapsed }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
      </div>
    </button>
    <div v-if="!collapsed" class="node-detail__body">
      <dl v-if="snapshot" class="node-detail__ids">
        <div><dt>run_id</dt><dd>{{ snapshot.run_id }}</dd></div><div><dt>trace_id</dt><dd>{{ snapshot.trace_id }}</dd></div>
        <div><dt>节点事件</dt><dd>{{ nodeEvents.length }}</dd></div><div><dt>执行 / 回退模式</dt><dd>{{ modeSummary }}</dd></div>
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
        <article class="node-detail__events">
          <h3>节点事件</h3>
          <ul v-if="nodeEvents.length">
            <li v-for="event in nodeEvents" :key="event.event_id">
              <time>{{ formatTime(event.created_at) }}</time><strong>{{ event.event_type }}</strong><span>{{ event.status }} · {{ event.display_name }}</span>
            </li>
          </ul>
          <p v-else>尚未收到当前节点的真实事件。</p>
        </article>
      </div>
      <div v-if="strategyPlan" class="node-detail__plan">
        <h3>招聘策略执行计划</h3>
        <p><b>generation_mode</b>{{ strategyPlan.generation_mode }}</p>
        <p><b>model_name</b>{{ strategyPlan.model_name || '未使用模型' }}</p>
        <p><b>fallback_used</b>{{ strategyPlan.fallback_used }}</p>
        <p><b>required_nodes</b>{{ strategyPlan.required_nodes.join(' → ') }}</p>
        <p><b>executed_nodes</b>{{ strategyPlan.executed_nodes.join('、') }}</p>
        <p><b>skipped_nodes</b>{{ strategyPlan.skipped_nodes.join('、') }}</p>
        <ul><li v-for="note in strategyPlan.plan_notes" :key="note">{{ note }}</li></ul>
      </div>
      <div v-else-if="nodeStatus === AgentNodeStatus.SKIPPED" class="node-detail__empty">
        {{ skippedSummary }}
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  AgentEventType,
  AgentNodeStatus,
  type AgentEvent,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';

const props=defineProps<{ snapshot:RecruitmentRunSnapshot|null; nodeName:string }>();
const collapsed = ref(false);
const definitions:Record<string,{label:string;task:string}>={
  recruitment_strategy:{label:'招聘策略 Agent',task:'读取已校验招聘目标与工作流元数据，生成当前阶段结构化执行计划。'},
  resume_parser:{label:'简历解析 Agent',task:'从白名单结构化字段和安全简历片段提取事实、缺失项与可定位证据。'},
  job_match:{label:'岗位匹配 Agent',task:'本阶段执行确定性评分与技能缺口分析。'},
  interview_evaluation:{label:'面试评估 Agent',task:'仅使用真实结构化面试数据；无真实结构化评价时跳过。'},
  decision_review:{label:'决策审查 Agent',task:'本阶段执行规则式证据和风险审查。'},
  hr_report:{label:'HR 最终报告',task:'本阶段执行结构化规则汇总，并将最终决定保留给 HR。'},
};
const metadata=computed(()=>definitions[props.nodeName]||{label:'节点详情',task:'未知节点'});
const nodeStatus=computed(()=>props.snapshot?.nodes[props.nodeName]||AgentNodeStatus.WAITING);
const nodeEvents=computed(()=>props.snapshot?.events.filter((event)=>event.node_name===props.nodeName)||[]);
const strategyPlan=computed(()=>props.nodeName==='recruitment_strategy' ? props.snapshot?.execution_plan||null : null);
const fallbackUsed=computed(()=>nodeEvents.value.some((event)=>event.fallback_used));
const skipReason=computed(()=>{
  const event=[...nodeEvents.value].reverse().find((item)=>item.status===AgentNodeStatus.SKIPPED);
  const directReason=event?.summary.skip_reason??event?.summary.reason;
  if(typeof directReason==='string') return directReason;
  const reasons=event?.summary.skip_reasons;
  if(reasons&&typeof reasons==='object') {
    const nodeReason=(reasons as Record<string,unknown>)[props.nodeName];
    if(typeof nodeReason==='string') return nodeReason;
  }
  return props.nodeName==='interview_evaluation' ? 'STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE' : '未提供跳过原因';
});
const skippedSummary=computed(()=>props.nodeName==='interview_evaluation'
  ? `节点已跳过（${skipReason.value}）：未生成面试评分或结论，决策审查将把缺少真实面试评价标记为待人工补充。`
  : `节点已跳过（${skipReason.value}），不展示其他节点结果作为本节点结果。`);
const modeSummary=computed(()=>{
  const snapshot=props.snapshot;
  if(!snapshot) return '等待真实运行结果';
  const modes:string[]=[];
  if(props.nodeName==='recruitment_strategy') {
    if(snapshot.execution_plan?.current_phase) modes.push(snapshot.execution_plan.current_phase);
    if(snapshot.knowledge_summary?.retrieval_mode) modes.push(snapshot.knowledge_summary.retrieval_mode);
  }
  if(props.nodeName==='resume_parser') modes.push(...Object.values(snapshot.candidate_profiles).map((profile)=>profile.extraction_mode));
  if(props.nodeName==='job_match') modes.push(...Object.values(snapshot.job_matches||{}).map((match)=>match.scoring_mode));
  if(props.nodeName==='decision_review') modes.push(...Object.values(snapshot.decision_reviews||{}).map((review)=>review.review_mode));
  if(props.nodeName==='hr_report'&&snapshot.report?.generation_mode) modes.push(snapshot.report.generation_mode);
  if(props.nodeName==='interview_evaluation'&&nodeStatus.value===AgentNodeStatus.SKIPPED) modes.push(skipReason.value);
  const unique=[...new Set(modes.filter(Boolean))];
  if(unique.length) return unique.join('、');
  return fallbackUsed.value ? 'fallback_used=true' : '未使用回退';
});
const inputSummary=computed(()=>formatSummary(findEvent([
  AgentEventType.AGENT_THINKING,AgentEventType.AGENT_STARTED,
])?.summary,nodeStatus.value===AgentNodeStatus.SKIPPED
  ? `无可用结构化输入（${skipReason.value}）`
  : '等待真实节点输入事件'));
const currentAction=computed(()=>{
  const event=[...nodeEvents.value].reverse().find((item)=>typeof item.summary.current_action==='string');
  return typeof event?.summary.current_action==='string' ? event.summary.current_action : nodeStatus.value===AgentNodeStatus.SKIPPED ? skippedSummary.value : '等待真实运行事件';
});
const toolSummary=computed(()=>{
  const tools=nodeEvents.value.map((event)=>event.tool_name).filter((name):name is string=>Boolean(name));
  return tools.length ? [...new Set(tools)].join('、') : '本阶段未调用';
});
const sourceSummary=computed(()=>{
  const count=nodeEvents.value.reduce((max,event)=>Math.max(max,event.source_count),0);
  const snapshot=props.snapshot;
  const sources=props.nodeName==='job_match'
    ? Object.values(snapshot?.job_matches||{}).flatMap((match)=>match.knowledge_sources)
    : props.nodeName==='hr_report'
      ? snapshot?.report?.knowledge_sources||[]
      : count
        ? snapshot?.sources||[]
        : [];
  const unique=[...new Map(sources.map((source)=>[source.source_id,source])).values()];
  if(unique.length) return unique.map((source)=>`${source.title}（${source.source_id}）`).join('、');
  return count ? `已关联 ${count} 个真实来源` : '本阶段未检索或关联来源';
});
const intermediateSummary=computed(()=>formatSummary(findEvent([AgentEventType.INTERMEDIATE_RESULT])?.summary,'本阶段无中间结果'));
const finalSummary=computed(()=>formatSummary(findEvent([
  AgentEventType.AGENT_COMPLETED,AgentEventType.REVIEW_COMPLETED,AgentEventType.REPORT_GENERATED,
])?.summary,nodeStatus.value===AgentNodeStatus.SKIPPED?skippedSummary.value:'尚无真实最终结论'));
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
function formatTime(value:string):string {
  return new Date(value).toLocaleTimeString('zh-CN',{hour12:false});
}
function safeDetail(value:unknown):string { return typeof value==='string' ? value : ''; }
</script>

<style scoped>
.node-detail { border:1px solid var(--color-line); border-radius:var(--radius-md); background:var(--color-surface); box-shadow:var(--shadow-card); }
.node-detail__toggle { display:flex; align-items:flex-end; justify-content:space-between; gap:16px; width:100%; padding:12px; border:none; background:none; color:inherit; cursor:pointer; }
.node-detail__toggle span { color:var(--color-primary); font-size:12px; font-weight:800; display:block; text-align:left; }
.node-detail h2 { margin:5px 0 0; text-align:left; }
.node-detail__toggle-meta { display:flex; align-items:center; gap:8px; flex-shrink:0; }
.node-detail__toggle-meta strong { color:var(--color-muted); font-size:12px; white-space:nowrap; }
.node-detail__chevron { color:var(--color-subtle); transition:transform 0.25s ease; }
.node-detail__chevron--collapsed { transform:rotate(-90deg); }
.node-detail__body { display:grid; gap:16px; padding:0 22px 22px; }
.node-detail--collapsed { /* collapsed — toggle padding handles the height */ }.node-detail__ids { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:0; }.node-detail__ids div { min-width:0; padding:11px; border-radius:10px; background:var(--color-surface-soft); }.node-detail dt { color:var(--color-subtle); font-size:11px; }.node-detail dd { overflow:hidden; margin:5px 0 0; color:var(--color-text); font-size:12px; font-weight:800; text-overflow:ellipsis; }.node-detail__grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }.node-detail article,.node-detail__plan { min-width:0; padding:14px; border:1px solid var(--color-line); border-radius:12px; }.node-detail article h3,.node-detail__plan h3 { margin:0 0 10px; font-size:13px; }.node-detail article p { margin:0; color:var(--color-muted); font-size:12px; line-height:1.6; }.node-detail article pre { overflow:auto; max-height:180px; margin:0; color:var(--color-muted); font:11px/1.5 ui-monospace,monospace; white-space:pre-wrap; }.node-detail__events { grid-column:span 2; }.node-detail__events ul { display:grid; gap:6px; margin:0; padding:0; list-style:none; }.node-detail__events li { display:grid; grid-template-columns:72px 160px 1fr; gap:8px; padding:8px; border-radius:8px; background:var(--color-surface-soft); font-size:11px; }.node-detail__events time { color:var(--color-subtle); }.node-detail__events span { color:var(--color-muted); }.node-detail__plan p { display:grid; grid-template-columns:130px 1fr; margin:7px 0; color:var(--color-muted); font-size:13px; }.node-detail__plan b { color:var(--color-text); }.node-detail__plan ul { margin:12px 0 0; color:var(--color-muted); }.node-detail__empty { color:var(--color-muted); }
@media(max-width:850px){.node-detail__ids,.node-detail__grid{grid-template-columns:1fr 1fr}} @media(max-width:560px){.node-detail__ids,.node-detail__grid{grid-template-columns:1fr}.node-detail__events{grid-column:auto}.node-detail__events li{grid-template-columns:1fr}.node-detail__plan p{grid-template-columns:1fr}}
</style>
