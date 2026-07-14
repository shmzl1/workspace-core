<template>
  <section class="sprint23-results">
    <header class="sprint23-results__heading">
      <div><span>招聘决策</span><h2>岗位匹配、决策审查与 HR 报告</h2></div>
      <strong>确定性结果与智能叙述</strong>
    </header>

    <section class="result-section">
      <header class="result-section__heading">
        <div><span>01</span><h3>岗位匹配结果</h3></div>
        <strong>{{ jobMatches.length }} 名候选人</strong>
      </header>
      <div v-if="jobMatches.length" class="result-grid">
        <article v-for="match in jobMatches" :key="match.candidate_id" class="result-card">
          <header class="result-card__heading">
            <div><span>候选人</span><h4>{{ candidateLabel(match.candidate_id) }}</h4></div>
            <span :class="['status-chip', jobMatchReviewPending(match) ? 'status-chip--review' : 'status-chip--complete']">
              {{ jobMatchReviewPending(match) ? '需要人工复核' : jobMatchReviewApproved(match) ? '已通过 HR 审查' : '评分结果已返回' }}
            </span>
          </header>

          <p v-if="match.overall_score === null || match.job_match_score === null" class="score-unavailable">
            确定性评分暂不可用，请人工复核
          </p>
          <dl class="metric-grid">
            <div><dt>综合分</dt><dd>{{ formatScore(match.overall_score) }}</dd></div>
            <div><dt>岗位匹配分</dt><dd>{{ formatScore(match.job_match_score) }}</dd></div>
            <div><dt>必备条件</dt><dd>{{ booleanLabel(match.must_have_passed, '通过', '未通过') }}</dd></div>
            <div><dt>证据数量</dt><dd>{{ match.evidence_ids.length }}</dd></div>
            <div><dt>知识来源</dt><dd>{{ match.knowledge_sources.length }}</dd></div>
            <div><dt>评分模式</dt><dd>{{ match.scoring_mode }}</dd></div>
          </dl>

          <div class="detail-block">
            <h5>五维分数</h5>
            <div v-if="dimensionEntries(match).length" class="dimension-grid">
              <div v-for="[dimension, score] in dimensionEntries(match)" :key="dimension">
                <span>{{ dimensionLabel(dimension) }}</span><strong>{{ formatScore(score) }}</strong>
              </div>
            </div>
            <p v-else class="empty-inline">后端未返回维度分数。</p>
          </div>

          <div class="detail-columns">
            <div class="detail-block">
              <h5>已匹配技能</h5>
              <div v-if="match.matched_skills.length" class="tag-list tag-list--matched">
                <span v-for="skill in match.matched_skills" :key="skill">{{ skill }}</span>
              </div>
              <p v-else class="empty-inline">暂无有证据支持的匹配技能。</p>
            </div>
            <div class="detail-block">
              <h5>缺失技能</h5>
              <div v-if="match.missing_skills.length" class="tag-list tag-list--missing">
                <span v-for="skill in match.missing_skills" :key="skill">{{ skill }}</span>
              </div>
              <p v-else class="empty-inline">未标记缺失技能。</p>
            </div>
          </div>

          <div class="detail-block">
            <h5>建议面试问题</h5>
            <ul v-if="match.suggested_interview_questions.length" class="compact-list">
              <li v-for="question in match.suggested_interview_questions" :key="question">{{ question }}</li>
            </ul>
            <p v-else class="empty-inline">当前真实结果未生成建议问题。</p>
          </div>
          <p class="recommendation"><b>建议动作</b>{{ match.recommended_action || '等待后端建议' }}</p>
          <p class="contract-line"><b>requires_review</b>{{ match.requires_review ? 'true' : 'false' }}</p>
        </article>
      </div>
      <p v-else class="empty-state">运行到岗位匹配节点后显示真实确定性结果，不使用静态样例。</p>
      <div v-if="jobMatchApprovalPending || jobMatchApprovalSubmitted || jobMatchApprovalError" class="review-approval">
        <button v-if="jobMatchApprovalPending && !jobMatchApprovalSubmitted" type="button" :disabled="jobMatchApproving" @click="approveJobMatch">
          审查通过
        </button>
        <p v-if="jobMatchApprovalSubmitted">
          {{ decisionReviewApprovalPending ? '岗位匹配审查已通过，请继续审查决策审查结果。' : '岗位匹配审查已通过，正在生成 HR 最终报告…' }}
        </p>
        <p v-else-if="jobMatchApprovalError" class="review-approval__error">{{ jobMatchApprovalError }}</p>
      </div>
    </section>

    <section class="result-section">
      <header class="result-section__heading">
        <div><span>02</span><h3>决策审查结果</h3></div>
        <strong>{{ decisionReviews.length }} 名候选人</strong>
      </header>
      <div v-if="decisionReviews.length" class="result-grid">
        <article v-for="review in decisionReviews" :key="review.candidate_id" class="result-card">
          <header class="result-card__heading">
            <div><span>候选人</span><h4>{{ candidateLabel(review.candidate_id) }}</h4></div>
            <span :class="['status-chip', decisionReviewPending(review) ? 'status-chip--review' : 'status-chip--complete']">
              {{ decisionReviewPending(review) ? '需要人工复核' : decisionReviewApproved(review) ? '已通过 HR 审查' : '审查结果已返回' }}
            </span>
          </header>
          <dl class="metric-grid metric-grid--review">
            <div><dt>可信度</dt><dd>{{ formatConfidence(review.confidence) }}</dd></div>
            <div><dt>审查模式</dt><dd>{{ review.review_mode }}</dd></div>
            <div><dt>确定性评分保留</dt><dd>{{ review.deterministic_score_preserved ? '是' : '否，请核对' }}</dd></div>
          </dl>

          <div class="detail-block">
            <h5>审查发现</h5>
            <ul v-if="review.findings.length" class="finding-list">
              <li v-for="(finding, index) in review.findings" :key="`${finding.code}-${index}`">
                <span :class="['severity-chip', `severity-chip--${finding.severity.toLowerCase()}`]">{{ finding.severity }}</span>
                <div><strong>{{ finding.code }}</strong><p>{{ finding.summary }}</p><small>证据 {{ finding.evidence_ids.length }} 条</small></div>
              </li>
            </ul>
            <p v-else class="empty-inline">后端未返回审查发现。</p>
          </div>

          <div class="detail-columns">
            <div class="detail-block">
              <h5>风险标签</h5>
              <div v-if="review.risk_tags.length" class="tag-list tag-list--missing">
                <span v-for="tag in review.risk_tags" :key="tag">{{ tag }}</span>
              </div>
              <p v-else class="empty-inline">未标记风险标签。</p>
            </div>
            <div class="detail-block">
              <h5>Agent 分歧</h5>
              <ul v-if="review.agent_disagreements.length" class="compact-list">
                <li v-for="item in review.agent_disagreements" :key="item">{{ item }}</li>
              </ul>
              <p v-else class="empty-inline">未记录 Agent 分歧。</p>
            </div>
          </div>
          <p class="recommendation"><b>建议动作</b>{{ review.recommended_action || '等待后端建议' }}</p>
        </article>
      </div>
      <p v-else class="empty-state">运行到决策审查节点后显示真实规则审查结果，不使用静态样例。</p>
      <div v-if="decisionReviewApprovalPending || decisionReviewApprovalSubmitted || decisionReviewApprovalError" class="review-approval">
        <button v-if="decisionReviewApprovalPending && !decisionReviewApprovalSubmitted" type="button" :disabled="decisionReviewApproving" @click="approveDecisionReview">
          审查通过
        </button>
        <p v-if="decisionReviewApprovalSubmitted">
          {{ jobMatchApprovalPending ? '决策审查已通过，请继续审查岗位匹配结果。' : '决策审查已通过，正在生成 HR 最终报告…' }}
        </p>
        <p v-else-if="decisionReviewApprovalError" class="review-approval__error">{{ decisionReviewApprovalError }}</p>
      </div>
    </section>

    <section class="result-section">
      <header class="result-section__heading">
        <div><span>03</span><h3>HR 最终报告</h3></div>
        <strong>{{ report?.generation_mode || '等待生成' }}</strong>
      </header>
      <div v-if="report" class="report-grid">
        <article class="report-card report-card--wide">
          <h4>报告摘要</h4>
          <p>{{ report.executive_summary || '当前使用确定性报告摘要。' }}</p>
          <small>模型：{{ report.model_name || '未使用模型' }} · fallback_used：{{ report.fallback_used }}</small>
        </article>
        <article class="report-card">
          <h4>候选人排序</h4>
          <ol v-if="report.candidate_rankings.length" class="ranking-list">
            <li v-for="(candidateId, index) in report.candidate_rankings" :key="candidateId">
              <span>{{ index + 1 }}</span><strong>{{ candidateLabel(candidateId) }}</strong><small>{{ rankingScore(candidateId) }}</small>
            </li>
          </ol>
          <p v-else class="empty-inline">报告未返回候选人排序。</p>
        </article>

        <article class="report-card">
          <h4>候选人审查摘要</h4>
          <div v-if="report.candidate_reviews.length" class="review-summary-list">
            <div v-for="review in report.candidate_reviews" :key="review.candidate_id">
              <strong>{{ candidateLabel(review.candidate_id) }}</strong>
              <span>可信度：{{ formatConfidence(review.confidence) }}</span>
              <p>{{ review.recommended_action || '等待后端建议' }}</p>
              <small>{{ findingCodes(review) }}</small>
            </div>
          </div>
          <p v-else class="empty-inline">报告未返回候选人审查摘要。</p>
        </article>

        <article class="report-card">
          <h4>企业知识</h4>
          <strong class="source-count">{{ report.knowledge_sources.length }}</strong>
          <p>个真实来源进入本次结构化报告。</p>
          <small>generation_mode：{{ report.generation_mode }}</small>
        </article>

        <article class="report-card">
          <h4>人才缺口</h4>
          <ul v-if="report.talent_gaps.length" class="compact-list">
            <li v-for="gap in report.talent_gaps" :key="gap">{{ gap }}</li>
          </ul>
          <p v-else class="empty-inline">当前报告未标记人才缺口。</p>
        </article>

        <article class="report-card report-card--wide">
          <h4>下一步动作</h4>
          <ul v-if="report.next_actions.length" class="compact-list">
            <li v-for="action in report.next_actions" :key="action">{{ action }}</li>
          </ul>
          <p v-else class="empty-inline">当前报告未返回下一步动作。</p>
        </article>

        <article class="report-card">
          <h4>风险摘要</h4>
          <ul v-if="report.risk_summary.length" class="compact-list">
            <li v-for="risk in report.risk_summary" :key="risk">{{ risk }}</li>
          </ul>
          <p v-else class="empty-inline">当前没有模型增强风险摘要。</p>
        </article>

        <article class="report-card">
          <h4>缺失信息</h4>
          <ul v-if="report.missing_information.length" class="compact-list">
            <li v-for="item in report.missing_information" :key="item">{{ item }}</li>
          </ul>
          <p v-else class="empty-inline">未标记额外缺失信息。</p>
        </article>

        <div class="human-decision">
          <div><span>人工决策边界</span><strong>最终决定由 HR 完成</strong></div>
          <p>{{ report.requires_human_decision ? '本报告仅提供建议与待复核信息，不代表已录用或已淘汰。' : '报告未标记人工决定，请核对后端结果。' }}</p>
        </div>
      </div>
      <p v-else class="empty-state">HR 报告尚未生成；此处只显示真实 Run 返回的报告，不使用静态样例。</p>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  approveDecisionReview as submitDecisionReviewApproval,
  approveJobMatchReview as submitJobMatchReviewApproval,
} from '../../../../shared/api/modules/agent';
import type {
  DecisionReviewSummary,
  JobMatchSummary,
  RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';
import { AgentNodeStatus } from '../../../../shared/agent/contracts';

const props = withDefaults(defineProps<{
  snapshot: RecruitmentRunSnapshot | null;
  candidateNames?: Record<number, string>;
}>(), {
  candidateNames: () => ({}),
});

const numberFormatter = new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 2 });
const dimensionLabels: Record<string, string> = {
  skill_match: '技能匹配',
  skill: '技能匹配',
  skills: '技能',
  experience: '经验匹配',
  education: '教育背景',
  projects: '项目经历',
  project: '项目经历',
  achievements: '可量化成果',
  bonus: '加分项',
  risk: '风险维度',
};

const jobMatches = computed(() => Object.values(props.snapshot?.job_matches || {})
  .sort((left, right) => left.candidate_id - right.candidate_id));
const decisionReviews = computed(() => Object.values(props.snapshot?.decision_reviews || {})
  .sort((left, right) => left.candidate_id - right.candidate_id));
const report = computed(() => props.snapshot?.report || null);
const jobMatchApproving = ref(false);
const jobMatchApprovalSubmitted = ref(false);
const jobMatchApprovalError = ref('');
const decisionReviewApproving = ref(false);
const decisionReviewApprovalSubmitted = ref(false);
const decisionReviewApprovalError = ref('');
const jobMatchApprovalPending = computed(() => {
  const snapshot = props.snapshot;
  if (!snapshot || snapshot.report !== null) return false;
  if (snapshot.nodes.hr_report !== AgentNodeStatus.WAITING) return false;
  return snapshot.nodes.job_match === AgentNodeStatus.NEEDS_REVIEW;
});
const decisionReviewApprovalPending = computed(() => {
  const snapshot = props.snapshot;
  if (!snapshot || snapshot.report !== null) return false;
  if (snapshot.nodes.hr_report !== AgentNodeStatus.WAITING) return false;
  return snapshot.nodes.decision_review === AgentNodeStatus.NEEDS_REVIEW;
});

watch(() => props.snapshot?.run_id, () => {
  jobMatchApproving.value = false;
  jobMatchApprovalSubmitted.value = false;
  jobMatchApprovalError.value = '';
  decisionReviewApproving.value = false;
  decisionReviewApprovalSubmitted.value = false;
  decisionReviewApprovalError.value = '';
});

async function approveJobMatch(): Promise<void> {
  if (!props.snapshot || jobMatchApproving.value) return;
  jobMatchApproving.value = true;
  jobMatchApprovalSubmitted.value = false;
  jobMatchApprovalError.value = '';
  try {
    await submitJobMatchReviewApproval(props.snapshot.run_id);
    jobMatchApprovalSubmitted.value = true;
  } catch (error) {
    jobMatchApprovalError.value = error instanceof Error ? error.message : '岗位匹配审查提交失败，请稍后重试。';
  } finally {
    jobMatchApproving.value = false;
  }
}

async function approveDecisionReview(): Promise<void> {
  if (!props.snapshot || decisionReviewApproving.value) return;
  decisionReviewApproving.value = true;
  decisionReviewApprovalSubmitted.value = false;
  decisionReviewApprovalError.value = '';
  try {
    await submitDecisionReviewApproval(props.snapshot.run_id);
    decisionReviewApprovalSubmitted.value = true;
  } catch (error) {
    decisionReviewApprovalError.value = error instanceof Error ? error.message : '决策审查提交失败，请稍后重试。';
  } finally {
    decisionReviewApproving.value = false;
  }
}

function candidateLabel(candidateId: number): string {
  return props.candidateNames[candidateId] || `候选人 #${candidateId}`;
}

function formatScore(value: number | null): string {
  return value === null || !Number.isFinite(value) ? '不可用' : `${numberFormatter.format(value)} 分`;
}

function formatConfidence(value: number | null): string {
  return value === null || !Number.isFinite(value) ? '不可用' : `${numberFormatter.format(value)}%`;
}

function booleanLabel(value: boolean | null, truthy: string, falsy: string): string {
  if (value === null) return '无法判断';
  return value ? truthy : falsy;
}

function dimensionEntries(match: JobMatchSummary): [string, number][] {
  return Object.entries(match.dimension_scores);
}

function dimensionLabel(dimension: string): string {
  return dimensionLabels[dimension] || dimension;
}

function matchNeedsReview(match: JobMatchSummary): boolean {
  return match.requires_review || match.overall_score === null || match.job_match_score === null;
}

function jobMatchReviewPending(match: JobMatchSummary): boolean {
  return matchNeedsReview(match)
    && props.snapshot?.nodes.job_match === AgentNodeStatus.NEEDS_REVIEW;
}

function jobMatchReviewApproved(match: JobMatchSummary): boolean {
  return matchNeedsReview(match)
    && props.snapshot?.nodes.job_match === AgentNodeStatus.COMPLETED;
}

function reviewNeedsHuman(review: DecisionReviewSummary): boolean {
  return review.findings.some((finding) => finding.requires_human_review);
}

function decisionReviewPending(review: DecisionReviewSummary): boolean {
  return reviewNeedsHuman(review)
    && props.snapshot?.nodes.decision_review === AgentNodeStatus.NEEDS_REVIEW;
}

function decisionReviewApproved(review: DecisionReviewSummary): boolean {
  return reviewNeedsHuman(review)
    && props.snapshot?.nodes.decision_review === AgentNodeStatus.COMPLETED;
}

function rankingScore(candidateId: number): string {
  const match = props.snapshot?.job_matches[String(candidateId)];
  return match ? formatScore(match.overall_score) : '无确定性评分';
}

function findingCodes(review: DecisionReviewSummary): string {
  return review.findings.length
    ? `审查项：${review.findings.map((finding) => finding.code).join('、')}`
    : '未返回审查项';
}
</script>

<style scoped>
.sprint23-results { display:grid; gap:18px; padding:22px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:#fff; box-shadow:var(--shadow-card); }
.sprint23-results__heading,.result-section__heading,.result-card__heading { display:flex; align-items:flex-end; justify-content:space-between; gap:16px; }
.sprint23-results__heading span,.result-section__heading span,.result-card__heading>div>span { color:var(--color-primary); font-size:11px; font-weight:900; }
.sprint23-results h2,.sprint23-results h3,.sprint23-results h4,.sprint23-results h5 { margin:0; }
.sprint23-results h2 { margin-top:5px; }.sprint23-results__heading>strong,.result-section__heading>strong { color:var(--color-muted); font-size:12px; }
.result-section { display:grid; gap:14px; padding:16px; border:1px solid var(--color-line); border-radius:14px; background:var(--color-surface-soft); }
.result-section__heading>div { display:flex; align-items:center; gap:9px; }.result-section__heading>div>span { display:grid; width:26px; height:26px; place-items:center; border-radius:50%; background:var(--color-primary-soft); }
.result-grid,.report-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }.result-card,.report-card { min-width:0; padding:15px; border:1px solid var(--color-line); border-radius:12px; background:#fff; }
.result-card { display:grid; gap:14px; }.result-card__heading h4 { margin-top:4px; font-size:16px; }.status-chip,.severity-chip { display:inline-flex; align-items:center; width:max-content; border-radius:999px; font-size:10px; font-weight:900; }
.status-chip { padding:7px 9px; }.status-chip--complete { background:#dcfce7; color:#166534; }.status-chip--review { background:#ffedd5; color:#9a3412; }
.score-unavailable { margin:0; padding:10px 12px; border:1px solid #fdba74; border-radius:10px; background:#fff7ed; color:#9a3412; font-size:12px; font-weight:800; }
.metric-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:7px; margin:0; }.metric-grid--review { grid-template-columns:repeat(3,minmax(0,1fr)); }.metric-grid div { min-width:0; padding:9px; border-radius:9px; background:var(--color-surface-soft); }.metric-grid dt { color:var(--color-subtle); font-size:10px; }.metric-grid dd { overflow-wrap:anywhere; margin:4px 0 0; color:var(--color-text); font-size:12px; font-weight:800; }
.detail-block { display:grid; gap:8px; }.detail-block h5 { color:var(--color-text); font-size:12px; }.detail-columns { display:grid; grid-template-columns:1fr 1fr; gap:12px; }.dimension-grid { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:6px; }.dimension-grid div { min-width:0; padding:9px; border-radius:9px; background:#f8fafc; }.dimension-grid span,.dimension-grid strong { display:block; overflow:hidden; text-overflow:ellipsis; }.dimension-grid span { color:var(--color-subtle); font-size:10px; white-space:nowrap; }.dimension-grid strong { margin-top:4px; color:var(--color-text); font-size:11px; }
.tag-list { display:flex; flex-wrap:wrap; gap:6px; }.tag-list span { padding:5px 7px; border-radius:999px; font-size:10px; font-weight:800; }.tag-list--matched span { background:#dcfce7; color:#166534; }.tag-list--missing span { background:#ffedd5; color:#9a3412; }
.compact-list { display:grid; gap:6px; margin:0; padding-left:18px; color:var(--color-muted); font-size:12px; line-height:1.55; }.empty-inline,.empty-state { margin:0; color:var(--color-muted); font-size:12px; }.empty-state { padding:18px; border:1px dashed var(--color-line); border-radius:10px; background:#fff; text-align:center; }
.recommendation,.contract-line { display:grid; grid-template-columns:90px 1fr; gap:8px; margin:0; color:var(--color-muted); font-size:12px; line-height:1.6; }.recommendation b,.contract-line b { color:var(--color-text); }.contract-line { padding-top:9px; border-top:1px solid var(--color-line); font-family:ui-monospace,monospace; }
.finding-list { display:grid; gap:7px; margin:0; padding:0; list-style:none; }.finding-list li { display:grid; grid-template-columns:auto 1fr; gap:9px; padding:9px; border-radius:9px; background:#f8fafc; }.finding-list strong { font-size:11px; }.finding-list p { margin:3px 0; color:var(--color-muted); font-size:11px; line-height:1.5; }.finding-list small { color:var(--color-subtle); font-size:10px; }.severity-chip { align-self:start; padding:4px 6px; background:#e2e8f0; color:#475569; }.severity-chip--high { background:#fee2e2; color:#b91c1c; }.severity-chip--medium { background:#ffedd5; color:#9a3412; }.severity-chip--low { background:#e0f2fe; color:#0369a1; }
.review-approval { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px; border:1px solid #bfdbfe; border-radius:10px; background:#eff6ff; }.review-approval button { padding:8px 12px; border:0; border-radius:8px; background:var(--color-primary); color:#fff; font-size:12px; font-weight:800; cursor:pointer; }.review-approval button:disabled { cursor:wait; opacity:.65; }.review-approval p { margin:0; color:#1e3a8a; font-size:12px; font-weight:700; }.review-approval .review-approval__error { color:#b91c1c; }
.report-card { display:grid; align-content:start; gap:10px; }.report-card--wide { grid-column:span 2; }.ranking-list { display:grid; gap:7px; margin:0; padding:0; list-style:none; }.ranking-list li { display:grid; grid-template-columns:28px 1fr auto; align-items:center; gap:8px; padding:8px; border-radius:9px; background:var(--color-surface-soft); }.ranking-list li>span { display:grid; width:24px; height:24px; place-items:center; border-radius:50%; background:var(--color-primary-soft); color:var(--color-primary); font-size:10px; font-weight:900; }.ranking-list strong { font-size:12px; }.ranking-list small { color:var(--color-muted); font-size:10px; }
.review-summary-list { display:grid; gap:8px; }.review-summary-list>div { padding:9px; border-radius:9px; background:var(--color-surface-soft); }.review-summary-list strong,.review-summary-list span,.review-summary-list small { display:block; }.review-summary-list strong { font-size:12px; }.review-summary-list span,.review-summary-list small { margin-top:3px; color:var(--color-subtle); font-size:10px; }.review-summary-list p,.report-card>p { margin:5px 0 0; color:var(--color-muted); font-size:11px; line-height:1.5; }.source-count { color:var(--color-primary); font-size:30px; }.report-card>small { color:var(--color-subtle); font-size:10px; }
.human-decision { grid-column:span 2; display:flex; align-items:center; justify-content:space-between; gap:20px; padding:15px; border:1px solid #bfdbfe; border-radius:12px; background:#eff6ff; }.human-decision span,.human-decision strong { display:block; }.human-decision span { color:var(--color-primary); font-size:10px; font-weight:900; }.human-decision strong { margin-top:4px; color:#1e3a8a; }.human-decision p { margin:0; color:#475569; font-size:12px; }
@media(max-width:1050px){.result-grid,.report-grid{grid-template-columns:1fr}.report-card--wide,.human-decision{grid-column:auto}.dimension-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:650px){.sprint23-results__heading,.result-section__heading,.result-card__heading,.human-decision{align-items:flex-start;flex-direction:column}.metric-grid,.metric-grid--review,.detail-columns,.dimension-grid{grid-template-columns:1fr 1fr}.ranking-list li{grid-template-columns:28px 1fr}.ranking-list small{grid-column:2}}
</style>
