<template>
  <section class="sprint22-results" :class="{ 'sprint22-results--collapsed': collapsed }">
    <button type="button" class="sprint22-results__toggle" @click="collapsed = !collapsed">
      <div><span>招聘评估</span><h2>策略、画像与企业知识</h2></div>
      <div class="sprint22-results__toggle-meta">
        <strong>可审计结构化输出</strong>
        <svg class="sprint22-results__chevron" :class="{ 'sprint22-results__chevron--collapsed': collapsed }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
      </div>
    </button>
    <div v-if="!collapsed" class="sprint22-results__body">
      <article>
        <h3>招聘策略卡片</h3>
        <dl>
          <div><dt>企业招聘目标</dt><dd>{{ goalLabel }}</dd></div>
          <div><dt>当前候选人数</dt><dd>{{ snapshot?.total_candidates || 0 }}</dd></div>
          <div><dt>专业 Agent</dt><dd>{{ plan?.required_nodes.join(' → ') || '等待真实执行计划' }}</dd></div>
          <div><dt>当前执行计划</dt><dd>{{ plan?.plan_notes.join('；') || '等待真实执行计划' }}</dd></div>
          <div><dt>是否重新解析</dt><dd>{{ plan?.resume_parse_required ? '是' : '否' }}</dd></div>
          <div><dt>已有面试候选人</dt><dd>{{ plan?.interview_candidate_ids.length || 0 }}</dd></div>
          <div><dt>已完成步骤</dt><dd>{{ completedSteps }}</dd></div>
          <div><dt>下一步动作</dt><dd>{{ plan?.next_actions.join('；') || '等待真实执行计划' }}</dd></div>
          <div><dt>生成模式</dt><dd>{{ plan?.generation_mode || '等待生成' }}</dd></div>
          <div><dt>模型</dt><dd>{{ plan?.model_name || '未使用模型' }}</dd></div>
          <div><dt>回退</dt><dd>{{ plan ? (plan.fallback_used ? '是' : '否') : '—' }}</dd></div>
          <div><dt>策略摘要</dt><dd>{{ plan?.strategy_summary || '使用确定性策略摘要' }}</dd></div>
        </dl>
      </article>
      <article>
        <h3>企业知识卡片</h3>
        <dl>
          <div><dt>标准版本</dt><dd>{{ knowledge?.standard_version || '等待检索' }}</dd></div>
          <div><dt>生效日期</dt><dd>{{ knowledge?.effective_date || '—' }}</dd></div>
          <div><dt>必备技能</dt><dd>{{ knowledge?.required_skills.join('、') || '未配置' }}</dd></div>
          <div><dt>加分技能</dt><dd>{{ knowledge?.preferred_skills.join('、') || '未配置' }}</dd></div>
          <div><dt>最低经验</dt><dd>{{ knowledge ? `${knowledge.min_experience_months} 个月` : '—' }}</dd></div>
          <div><dt>命中文档</dt><dd>{{ knowledge?.sources.length || 0 }}</dd></div>
          <div><dt>检索模式</dt><dd>{{ knowledge?.retrieval_mode || '等待检索' }}</dd></div>
          <div><dt>检索提示</dt><dd>{{ knowledge?.warnings.join('；') || '无' }}</dd></div>
        </dl>
      </article>
    </div>

    <section class="profile-panel" :class="{ 'profile-panel--collapsed': profileCollapsed }">
      <button type="button" class="profile-panel__toggle" @click="profileCollapsed = !profileCollapsed">
        <h3>简历解析卡片与证据面板</h3>
        <svg class="profile-panel__chevron" :class="{ 'profile-panel__chevron--collapsed': profileCollapsed }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
      </button>
      <div v-if="!profileCollapsed" class="profile-panel__body">
        <div v-if="profiles.length" class="profile-grid">
          <article v-for="profile in profiles" :key="profile.candidate_id" class="profile-card">
            <header><strong>候选人 #{{ profile.candidate_id }}</strong><span>{{ profile.extraction_mode }}</span></header>
            <dl>
              <div><dt>技能</dt><dd>{{ profile.skills.length }}</dd></div>
              <div><dt>项目</dt><dd>{{ profile.projects.length }}</dd></div>
              <div><dt>可量化成果</dt><dd>{{ profile.measurable_achievements.length }}</dd></div>
              <div><dt>缺失字段</dt><dd>{{ profile.missing_fields.length }}</dd></div>
              <div><dt>证据</dt><dd>{{ profile.evidence_items.length }}</dd></div>
              <div><dt>状态</dt><dd>{{ profile.fallback_used ? '确定性回退完成' : '解析完成' }}</dd></div>
            </dl>
            <p><b>标准化技能：</b>{{ profile.normalized_skills.join('、') || '未知' }}</p>
            <p><b>缺失项：</b>{{ profile.missing_fields.join('、') || '无' }}</p>
            <details v-for="evidence in profile.evidence_items" :key="evidence.evidence_id">
              <summary>{{ evidence.capability }} · {{ evidence.supports ? '支持' : '不支持/未知' }}</summary>
              <p>{{ evidence.excerpt }}</p>
              <small>区块：{{ evidence.source_section || '未知' }} · 可信度：{{ evidence.confidence ?? '未知' }}</small>
            </details>
          </article>
        </div>
        <p v-else class="empty-result">运行后显示真实候选人画像，不使用静态样例。</p>
      </div>
    </section>

    <section class="source-panel" :class="{ 'source-panel--collapsed': sourceCollapsed }">
      <button type="button" class="source-panel__toggle" @click="sourceCollapsed = !sourceCollapsed">
        <h3>企业知识来源</h3>
        <svg class="source-panel__chevron" :class="{ 'source-panel__chevron--collapsed': sourceCollapsed }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
      </button>
      <div v-if="!sourceCollapsed" class="source-panel__body">
        <div v-if="knowledge?.sources.length" class="source-grid">
          <article v-for="source in knowledge.sources" :key="source.source_id">
            <strong>{{ source.title }}</strong>
            <span>{{ source.document_type }} · {{ source.version }} · {{ source.effective_date }}</span>
            <p>{{ source.excerpt }}</p>
            <small>{{ source.source_id }} · 相关度 {{ source.relevance }}</small>
          </article>
        </div>
        <p v-else class="empty-result">尚未收到真实知识来源。</p>
      </div>
    </section>
    
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { AgentNodeStatus, type RecruitmentRunSnapshot } from '../../../../shared/agent/contracts';

const props=defineProps<{snapshot:RecruitmentRunSnapshot|null}>();
const collapsed = ref(false);
const profileCollapsed = ref(false);
const sourceCollapsed = ref(false);
const plan=computed(()=>props.snapshot?.execution_plan||null);
const knowledge=computed(()=>props.snapshot?.knowledge_summary||null);
const profiles=computed(()=>Object.values(props.snapshot?.candidate_profiles||{}));
const goalLabel=computed(()=>props.snapshot ? `${props.snapshot.goal.job_title} · ${props.snapshot.goal.target_headcount} 人` : '等待真实 Run');
const completedSteps=computed(()=>{
  const nodes=props.snapshot?.nodes||{};
  return ['recruitment_strategy','resume_parser']
    .filter((node)=>nodes[node]===AgentNodeStatus.COMPLETED)
    .join('、')||'尚未完成';
});
</script>

<style scoped>
.sprint22-results { border:1px solid var(--color-line); border-radius:var(--radius-md); background:var(--color-surface); box-shadow:var(--shadow-card); }
.sprint22-results__toggle { display:flex; align-items:flex-end; justify-content:space-between; gap:16px; width:100%; padding:12px; border:none; background:none; color:inherit; cursor:pointer; }
.sprint22-results__toggle span { color:var(--color-primary); font-size:12px; font-weight:800; display:block; text-align:left; }
.sprint22-results h2 { margin:5px 0 0; text-align:left; }
.sprint22-results__toggle-meta { display:flex; align-items:center; gap:8px; flex-shrink:0; }
.sprint22-results__toggle-meta strong { color:var(--color-muted); font-size:12px; white-space:nowrap; }
.sprint22-results__chevron { color:var(--color-subtle); transition:transform 0.25s ease; }
.sprint22-results__chevron--collapsed { transform:rotate(-90deg); }
.sprint22-results__body { display:grid; gap:16px; padding:0 22px 22px; }.sprint22-results__cards { display:grid; grid-template-columns:1fr 1fr; gap:12px; }.sprint22-results article,.profile-panel,.source-panel { padding:14px; border:1px solid var(--color-line); border-radius:12px; }.sprint22-results h3 { margin:0 0 12px; }.sprint22-results dl { display:grid; gap:7px; margin:0; }.sprint22-results dl div { display:grid; grid-template-columns:120px 1fr; gap:8px; }.sprint22-results dt { color:var(--color-subtle); font-size:11px; }.sprint22-results dd { margin:0; color:var(--color-text); font-size:12px; font-weight:700; }.profile-grid,.source-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }.profile-card header { display:flex; justify-content:space-between; gap:10px; }.profile-card header span { color:var(--color-primary); font-size:11px; }.profile-card dl { grid-template-columns:repeat(3,minmax(0,1fr)); margin:12px 0; }.profile-card dl div { display:block; padding:8px; border-radius:8px; background:var(--color-surface-soft); }.profile-card p,.source-grid p { color:var(--color-muted); font-size:12px; line-height:1.6; }.profile-card details { margin-top:7px; padding:8px; border-radius:8px; background:var(--color-surface-soft); }.profile-card summary { color:var(--color-text); font-size:12px; font-weight:700; cursor:pointer; }.profile-card small,.source-grid span,.source-grid small { display:block; margin-top:5px; color:var(--color-subtle); font-size:10px; }.source-grid article strong { display:block; }.empty-result { margin:0; color:var(--color-muted); }.profile-panel__toggle,.source-panel__toggle { display:flex; align-items:center; justify-content:space-between; width:100%; padding:0; border:none; background:none; color:inherit; cursor:pointer; }.profile-panel__toggle h3,.source-panel__toggle h3 { margin:0; }.profile-panel__chevron,.source-panel__chevron { color:var(--color-subtle); transition:transform 0.25s ease; flex-shrink:0; }.profile-panel__chevron--collapsed,.source-panel__chevron--collapsed { transform:rotate(-90deg); }.profile-panel__body,.source-panel__body { margin-top:12px; }
@media(max-width:900px){.sprint22-results__cards,.profile-grid,.source-grid{grid-template-columns:1fr}} @media(max-width:560px){.sprint22-results dl div{grid-template-columns:1fr}.profile-card dl{grid-template-columns:1fr 1fr}}
</style>
