<template>
  <section class="node-detail">
    <header><div><span>运行详情</span><h2>{{ nodeLabel }}</h2></div><strong>{{ nodeStatus }}</strong></header>
    <dl v-if="snapshot">
      <div><dt>run_id</dt><dd>{{ snapshot.run_id }}</dd></div><div><dt>trace_id</dt><dd>{{ snapshot.trace_id }}</dd></div>
      <div><dt>运行状态</dt><dd>{{ snapshot.status }}</dd></div><div><dt>候选人数</dt><dd>{{ snapshot.total_candidates }}</dd></div>
    </dl>
    <div v-if="plan" class="node-detail__plan">
      <h3>招聘策略执行计划</h3>
      <p><b>required_nodes</b>{{ plan.required_nodes.join(' → ') }}</p>
      <p><b>executed_nodes</b>{{ plan.executed_nodes.join('、') }}</p>
      <p><b>skipped_nodes</b>{{ plan.skipped_nodes.join('、') }}</p>
      <ul><li v-for="note in plan.plan_notes" :key="note">{{ note }}</li></ul>
    </div>
    <div v-else class="node-detail__empty">执行计划将在真实 PLAN_CREATED 事件后显示。</div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { AgentNodeStatus, type RecruitmentRunSnapshot } from '../../../../shared/agent/contracts';
const props=defineProps<{ snapshot:RecruitmentRunSnapshot|null; nodeName:string }>();
const labels:Record<string,string>={recruitment_strategy:'招聘策略 Agent',resume_parser:'简历解析 Agent',job_match:'岗位匹配 Agent',interview_evaluation:'面试评估 Agent',decision_review:'决策审查 Agent',hr_report:'HR 最终报告'};
const nodeLabel=computed(()=>labels[props.nodeName]||'节点详情');
const nodeStatus=computed(()=>props.snapshot?.nodes[props.nodeName]||AgentNodeStatus.WAITING);
const plan=computed(()=>props.snapshot?.execution_plan||null);
</script>

<style scoped>
.node-detail { display:grid; gap:16px; padding:22px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:#fff; box-shadow:var(--shadow-card); }.node-detail header { display:flex; align-items:flex-end; justify-content:space-between; }.node-detail header span { color:var(--color-primary); font-size:12px; font-weight:800; }.node-detail h2 { margin:5px 0 0; }.node-detail header strong { color:var(--color-muted); } dl { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:0; } dl div { min-width:0; padding:11px; border-radius:10px; background:var(--color-surface-soft); } dt { color:var(--color-subtle); font-size:11px; } dd { overflow:hidden; margin:5px 0 0; color:var(--color-text); font-size:12px; font-weight:800; text-overflow:ellipsis; }.node-detail__plan { padding:14px; border:1px solid var(--color-line); border-radius:12px; }.node-detail__plan h3 { margin:0 0 12px; }.node-detail__plan p { display:grid; grid-template-columns:130px 1fr; margin:7px 0; color:var(--color-muted); font-size:13px; }.node-detail__plan b { color:var(--color-text); }.node-detail__plan ul { margin:12px 0 0; color:var(--color-muted); }.node-detail__empty { color:var(--color-muted); } @media(max-width:850px){dl{grid-template-columns:1fr 1fr}} @media(max-width:520px){dl{grid-template-columns:1fr}.node-detail__plan p{grid-template-columns:1fr}}
</style>

