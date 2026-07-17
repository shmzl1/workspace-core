<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open && metadata"
        class="fixed inset-0 z-[9999] flex items-start justify-center overflow-y-auto bg-slate-950/60 p-3 backdrop-blur-sm sm:items-center sm:p-6"
        @click.self="emit('close')"
      >
        <section
          ref="dialogRef"
          class="my-auto flex max-h-[calc(100vh-1.5rem)] w-full max-w-5xl flex-col overflow-hidden rounded-[24px] border border-slate-200 bg-white shadow-2xl outline-none sm:max-h-[85vh]"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="dialogTitleId"
          tabindex="-1"
        >
          <header class="flex shrink-0 items-start justify-between gap-4 border-b border-slate-200 bg-white/95 px-5 py-4 backdrop-blur-md sm:px-7 sm:py-5">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded-full px-2.5 py-1 text-[11px] font-black tracking-wide" :class="statusClasses.badge">{{ status }}</span>
                <span class="font-mono text-xs text-slate-400">{{ nodeName }}</span>
              </div>
              <h2 :id="dialogTitleId" class="mt-2 text-xl font-black tracking-tight text-slate-900 sm:text-2xl">{{ metadata.title }}</h2>
              <p class="mt-1 text-sm text-slate-500">Agent 处理依据与可审计结果</p>
            </div>
            <button
              type="button"
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
              aria-label="关闭 Agent 处理依据"
              @click="emit('close')"
            >
              <X class="h-5 w-5" aria-hidden="true" />
            </button>
          </header>

          <div class="min-h-0 flex-1 overflow-y-auto px-4 py-5 sm:px-7 sm:py-6">
            <div class="rounded-2xl border border-indigo-100 bg-indigo-50/70 p-4 text-sm leading-6 text-indigo-800">
              <div class="flex items-start gap-3">
                <ShieldCheck class="mt-0.5 h-5 w-5 shrink-0 text-indigo-600" aria-hidden="true" />
                <p>为保护模型安全与候选人隐私，本页面仅展示结构化处理依据和可审计结果，不展示模型隐藏思维过程。</p>
              </div>
            </div>

            <section class="mt-6">
              <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
                <MetricCard label="本次执行动作" :value="currentAction" wide />
                <MetricCard label="执行时间" :value="durationLabel" />
                <MetricCard label="事件数量" :value="String(nodeEvents.length)" />
                <MetricCard label="调用工具" :value="String(toolNames.length)" />
                <MetricCard label="知识来源" :value="String(knowledgeSources.length)" />
                <MetricCard label="回退 / 复核" :value="`${fallbackUsed ? '是' : '否'} / ${requiresReview ? '是' : '否'}`" />
              </div>

              <div v-if="snapshot" class="mt-3 grid gap-3 sm:grid-cols-2">
                <div class="min-w-0 rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3">
                  <p class="text-[11px] font-semibold text-slate-400">run_id</p>
                  <p class="mt-1 truncate font-mono text-xs text-slate-700" :title="snapshot.run_id">{{ snapshot.run_id }}</p>
                </div>
                <div class="min-w-0 rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3">
                  <p class="text-[11px] font-semibold text-slate-400">trace_id</p>
                  <p class="mt-1 truncate font-mono text-xs text-slate-700" :title="snapshot.trace_id">{{ snapshot.trace_id }}</p>
                </div>
              </div>
            </section>

            <div class="mt-5 rounded-2xl border p-4 text-sm" :class="statusClasses.notice">
              <div class="flex items-start gap-3">
                <LoaderCircle v-if="status === AgentNodeStatus.RUNNING" class="mt-0.5 h-5 w-5 shrink-0 animate-spin" aria-hidden="true" />
                <CircleAlert v-else-if="status === AgentNodeStatus.FAILED || status === AgentNodeStatus.NEEDS_REVIEW" class="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
                <CircleDashed v-else class="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
                <div class="min-w-0">
                  <p class="font-bold">{{ statusMessage }}</p>
                  <p v-if="skipReason" class="mt-1 break-words text-xs">跳过原因：{{ skipReason }}</p>
                  <div v-if="failedError" class="mt-2 text-xs">
                    <p>{{ failedError.code }} · {{ failedError.message }}</p>
                    <pre v-if="safeFailedDetails" class="mt-2 overflow-x-auto whitespace-pre-wrap font-mono text-[11px]">{{ safeFailedDetails }}</pre>
                  </div>
                </div>
              </div>
            </div>

            <section class="mt-7">
              <SectionHeading :icon="UserCog" title="Agent 职责" />
              <p class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 text-sm leading-6 text-slate-700">{{ metadata.responsibility }}</p>
            </section>

            <section v-if="candidateRelated" class="mt-7">
              <SectionHeading :icon="Users" title="候选人范围" />
              <div v-if="candidateIds.length" class="flex flex-col gap-2 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 sm:flex-row sm:items-center">
                <label for="agent-candidate-selector" class="text-sm font-semibold text-slate-700">查看候选人</label>
                <select
                  id="agent-candidate-selector"
                  v-model.number="selectedCandidateId"
                  class="min-w-0 flex-1 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                >
                  <option v-for="candidateId in candidateIds" :key="candidateId" :value="candidateId">{{ candidateLabel(candidateId, candidateNames) }}</option>
                </select>
              </div>
              <div v-else class="rounded-2xl border border-dashed border-slate-300 bg-slate-50/60 p-5 text-center text-sm text-slate-500">
                当前 Snapshot 中没有候选人数据，未创建模拟候选人。
              </div>
            </section>

            <section class="mt-7">
              <SectionHeading :icon="ScanSearch" title="读取的信息" />
              <div v-if="snapshot && inputItems.length" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <DataCard v-for="item in inputItems" :key="item.label" :label="item.label" :value="item.value" :wide="item.wide" />
              </div>
              <div v-else class="rounded-2xl border border-dashed border-slate-300 bg-slate-50/60 p-5 text-sm text-slate-500">
                <p v-if="!snapshot">当前尚未执行招聘工作流。</p>
                <p class="mt-2">运行后预计读取：{{ metadata.expectedInputs.join('、') }}。</p>
              </div>
            </section>

            <section class="mt-7">
              <SectionHeading :icon="Wrench" title="处理方式与工具" />
              <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
                <div v-if="toolNames.length" class="flex flex-wrap gap-2">
                  <span v-for="toolName in toolNames" :key="toolName" class="rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700" :title="toolName">
                    {{ toolLabel(toolName) }}
                  </span>
                </div>
                <p v-else class="text-sm text-slate-500">当前节点尚无工具调用记录。</p>
                <dl v-if="processingItems.length" class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  <div v-for="item in processingItems" :key="item.label" class="rounded-xl border border-slate-200 bg-white p-3">
                    <dt class="text-[11px] text-slate-400">{{ item.label }}</dt>
                    <dd class="mt-1 break-words text-xs font-semibold text-slate-700">{{ displayValue(item.value) }}</dd>
                  </div>
                </dl>
                <div v-if="nodeName === 'job_match'" class="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-3 text-xs leading-5 text-blue-800">
                  <strong>确定性人工评分边界：</strong> DETERMINISTIC_HUMAN_ONLY。分数由公开确定性规则计算，不由大模型自由生成。
                </div>
              </div>
            </section>

            <section class="mt-7">
              <SectionHeading :icon="FileCheck2" title="处理结果" />
              <div v-if="snapshot && outputItems.length" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <DataCard v-for="item in outputItems" :key="item.label" :label="item.label" :value="item.value" :wide="item.wide" />
              </div>
              <div v-else class="rounded-2xl border border-dashed border-slate-300 bg-slate-50/60 p-5 text-sm text-slate-500">
                {{ outputEmptyMessage }}
              </div>
              <p v-if="nodeName === 'interview_evaluation' && status === AgentNodeStatus.SKIPPED" class="mt-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
                系统未发现真实结构化面试评分或面试官反馈，因此没有生成虚假的面试评价。
              </p>
            </section>

            <section class="mt-7">
              <SectionHeading :icon="Database" title="企业知识来源" />
              <AgentKnowledgeSourceList :sources="knowledgeSources" />
            </section>

            <section class="mt-7 pb-2">
              <SectionHeading :icon="Activity" title="本次执行记录" />
              <AgentEventTimeline :events="nodeEvents" :candidate-names="candidateNames" />
            </section>
          </div>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, nextTick, onBeforeUnmount, ref, watch, type Component } from 'vue';
import {
  Activity,
  CircleAlert,
  CircleDashed,
  Database,
  FileCheck2,
  LoaderCircle,
  ScanSearch,
  ShieldCheck,
  UserCog,
  Users,
  Wrench,
  X,
} from 'lucide-vue-next';
import {
  AgentNodeStatus,
  type AgentErrorInfo,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';
import AgentEventTimeline from './AgentEventTimeline.vue';
import AgentKnowledgeSourceList from './AgentKnowledgeSourceList.vue';
import {
  agentMetadata,
  candidateLabel,
  isAgentNodeName,
  latestStringSummary,
  mergeKnowledgeSources,
  nodeEventsFor,
  nodeStatusFor,
  resolveSkipReason,
  sanitizeStructuredValue,
  toolLabel,
  uniqueToolNames,
} from '../utils/agentProcessingBasis';

interface Props {
  open: boolean;
  nodeName: string | null;
  snapshot: RecruitmentRunSnapshot | null;
  candidateNames?: Record<number, string>;
}

interface DisplayItem {
  label: string;
  value: unknown;
  wide?: boolean;
}

const props = withDefaults(defineProps<Props>(), { candidateNames: () => ({}) });
const emit = defineEmits<{ close: [] }>();

const dialogRef = ref<HTMLElement | null>(null);
const selectedCandidateId = ref<number | null>(null);
let bodyOverflowBeforeDialog: string | null = null;

const metadata = computed(() => isAgentNodeName(props.nodeName) ? agentMetadata[props.nodeName] : null);
const dialogTitleId = computed(() => `agent-processing-basis-${props.nodeName || 'unknown'}`);
const nodeEvents = computed(() => nodeEventsFor(props.snapshot, props.nodeName));
const status = computed(() => nodeStatusFor(props.snapshot, props.nodeName));
const toolNames = computed(() => uniqueToolNames(nodeEvents.value));
const skipReason = computed(() => status.value === AgentNodeStatus.SKIPPED ? resolveSkipReason(props.nodeName, nodeEvents.value) : null);
const knowledgeSources = computed(() => mergeKnowledgeSources(props.snapshot, selectedCandidateId.value));
const candidateRelated = computed(() => ['resume_parser', 'job_match', 'decision_review', 'interview_evaluation'].includes(props.nodeName || ''));
const candidateIds = computed(() => {
  if (!props.snapshot || !candidateRelated.value) return [];
  return [...new Set(props.snapshot.candidate_ids)].sort((left, right) => left - right);
});
const currentProfile = computed(() => selectedCandidateId.value === null ? null : props.snapshot?.candidate_profiles[String(selectedCandidateId.value)] ?? null);
const currentMatch = computed(() => selectedCandidateId.value === null ? null : props.snapshot?.job_matches[String(selectedCandidateId.value)] ?? null);
const currentReview = computed(() => selectedCandidateId.value === null ? null : props.snapshot?.decision_reviews[String(selectedCandidateId.value)] ?? null);
const currentInterview = computed(() => selectedCandidateId.value === null ? null : props.snapshot?.interview_evaluations[String(selectedCandidateId.value)] ?? null);
const fallbackUsed = computed(() => {
  if (nodeEvents.value.some((event) => event.fallback_used)) return true;
  if (props.nodeName === 'recruitment_strategy') return Boolean(props.snapshot?.execution_plan?.fallback_used);
  if (props.nodeName === 'resume_parser') return Boolean(currentProfile.value?.fallback_used);
  if (props.nodeName === 'hr_report') return Boolean(props.snapshot?.report?.fallback_used);
  return false;
});
const requiresReview = computed(() => {
  if (status.value === AgentNodeStatus.NEEDS_REVIEW) return true;
  if (props.nodeName === 'job_match') return Boolean(currentMatch.value?.requires_review);
  if (props.nodeName === 'decision_review') return Boolean(currentReview.value?.findings.some((finding) => finding.requires_human_review));
  if (props.nodeName === 'interview_evaluation') return Boolean(currentInterview.value?.requires_review);
  if (props.nodeName === 'hr_report') return Boolean(props.snapshot?.report?.requires_human_decision);
  return false;
});
const currentAction = computed(() => latestStringSummary(nodeEvents.value, 'current_action') || nodeEvents.value.at(-1)?.display_name || (props.snapshot ? '等待节点事件' : '尚未运行'));
const durationLabel = computed(() => {
  const duration = [...nodeEvents.value].reverse().find((event) => event.duration_ms !== null)?.duration_ms;
  if (duration === undefined || duration === null) return '—';
  return duration >= 1000 ? `${(duration / 1000).toFixed(2)} 秒` : `${duration} ms`;
});
const failedError = computed<AgentErrorInfo | null>(() => {
  const eventError = [...nodeEvents.value].reverse().find((event) => event.error)?.error;
  return eventError ?? (status.value === AgentNodeStatus.FAILED ? props.snapshot?.error ?? null : null);
});
const safeFailedDetails = computed(() => {
  if (!failedError.value || Object.keys(failedError.value.details).length === 0) return null;
  const value = sanitizeStructuredValue(failedError.value.details);
  return value ? JSON.stringify(value, null, 2) : null;
});

const statusMessage = computed(() => {
  if (!props.snapshot) return '当前尚未执行招聘工作流。';
  const messages: Record<AgentNodeStatus, string> = {
    [AgentNodeStatus.WAITING]: '该 Agent 正在等待前置节点完成。',
    [AgentNodeStatus.RUNNING]: '该 Agent 正在运行，下面会实时展示已收到的可审计事件。',
    [AgentNodeStatus.COMPLETED]: '该 Agent 已完成本次处理。',
    [AgentNodeStatus.NEEDS_REVIEW]: '该 Agent 已产出结果，当前需要 HR 人工复核。',
    [AgentNodeStatus.FAILED]: '该 Agent 本次执行失败，请根据安全错误信息处理。',
    [AgentNodeStatus.SKIPPED]: '该 Agent 按工作流规则被跳过，并非执行失败。',
  };
  return messages[status.value];
});

const statusClasses = computed(() => {
  const classes: Record<AgentNodeStatus, { badge: string; notice: string }> = {
    [AgentNodeStatus.COMPLETED]: { badge: 'bg-emerald-50 text-emerald-700', notice: 'border-emerald-200 bg-emerald-50 text-emerald-800' },
    [AgentNodeStatus.RUNNING]: { badge: 'bg-blue-50 text-blue-700', notice: 'border-blue-200 bg-blue-50 text-blue-800' },
    [AgentNodeStatus.NEEDS_REVIEW]: { badge: 'bg-amber-50 text-amber-700', notice: 'border-amber-200 bg-amber-50 text-amber-800' },
    [AgentNodeStatus.FAILED]: { badge: 'bg-red-50 text-red-700', notice: 'border-red-200 bg-red-50 text-red-800' },
    [AgentNodeStatus.SKIPPED]: { badge: 'bg-slate-100 text-slate-600', notice: 'border-slate-200 bg-slate-50 text-slate-700' },
    [AgentNodeStatus.WAITING]: { badge: 'bg-slate-100 text-slate-500', notice: 'border-slate-200 bg-slate-50 text-slate-600' },
  };
  return classes[status.value];
});

const inputItems = computed<DisplayItem[]>(() => {
  const snapshot = props.snapshot;
  if (!snapshot) return [];
  switch (props.nodeName) {
    case 'recruitment_strategy':
      return [
        item('岗位名称', snapshot.job.job_title), item('部门', snapshot.job.department), item('招聘人数', snapshot.goal.target_headcount),
        item('截止日期', snapshot.goal.deadline), item('必须技能', snapshot.goal.required_skills, true), item('优先技能', snapshot.goal.preferred_skills, true),
        item('最低工作经验', `${snapshot.goal.min_experience_months} 个月`), item('评分阈值', snapshot.goal.score_threshold),
        item('可信度阈值', snapshot.goal.confidence_threshold), item('紧急程度', snapshot.goal.urgency), item('候选人数', snapshot.candidate_ids.length),
        item('企业招聘标准版本', snapshot.knowledge_summary?.standard_version), item('知识检索模式', snapshot.knowledge_summary?.retrieval_mode),
        item('岗位评分规则', snapshot.job_rubric, true),
      ];
    case 'resume_parser':
      return currentProfile.value ? [
        item('候选人', selectedCandidateLabel.value), item('候选人编号', selectedCandidateId.value),
        item('提取模式', currentProfile.value.extraction_mode), item('证据条目数', currentProfile.value.evidence_items.length),
      ] : [];
    case 'job_match':
      return [
        item('岗位名称', snapshot.goal.job_title), item('候选人', selectedCandidateLabel.value), item('评分阈值', snapshot.goal.score_threshold),
        item('岗位规则版本', snapshot.job_rubric?.version), item('岗位规则项数', snapshot.job_rubric?.requirements.length ?? 0),
        item('画像技能', currentProfile.value?.normalized_skills ?? currentProfile.value?.skills ?? [], true),
        item('企业标准版本', snapshot.knowledge_summary?.standard_version), item('知识检索模式', snapshot.knowledge_summary?.retrieval_mode),
      ];
    case 'decision_review':
      return [
        item('可信度阈值', snapshot.goal.confidence_threshold), item('候选人', selectedCandidateLabel.value),
        item('画像缺失字段', currentProfile.value?.missing_fields ?? [], true), item('综合得分', currentMatch.value?.overall_score),
        item('必备条件通过', currentMatch.value?.must_have_passed), item('面试评估状态', currentInterview.value?.status ?? '未提供真实结构化面试数据'),
      ];
    case 'hr_report':
      return [
        item('岗位名称', snapshot.goal.job_title), item('候选人数', snapshot.candidate_ids.length),
        item('岗位匹配结果数', Object.keys(snapshot.job_matches).length), item('决策审查结果数', Object.keys(snapshot.decision_reviews).length),
        item('知识来源数', knowledgeSources.value.length), item('知识检索模式', snapshot.knowledge_summary?.retrieval_mode),
      ];
    case 'interview_evaluation':
      return [
        item('候选人', selectedCandidateLabel.value),
        item('structured_interview_feedback_available', summaryValue('structured_interview_feedback_available') ?? Boolean(currentInterview.value)),
        item('interview_conclusion_generated', summaryValue('interview_conclusion_generated') ?? Boolean(currentInterview.value?.conclusion)),
      ];
    default:
      return [];
  }
});

const processingItems = computed<DisplayItem[]>(() => [
  ['当前目标', 'current_goal'], ['当前动作', 'current_action'], ['下一步动作', 'next_action'],
  ['评分模式', 'scoring_mode'], ['检索模式', 'retrieval_mode'], ['生成模式', 'generation_mode'],
].flatMap(([label, key]) => {
  const value = latestStringSummary(nodeEvents.value, key);
  return value ? [item(label, value)] : [];
}));

const outputItems = computed<DisplayItem[]>(() => {
  const snapshot = props.snapshot;
  if (!snapshot) return [];
  switch (props.nodeName) {
    case 'recruitment_strategy': {
      const plan = snapshot.execution_plan;
      if (!plan) return [];
      return [
        item('执行节点', plan.executed_nodes, true), item('跳过节点', plan.skipped_nodes, true), item('下一步动作', plan.next_actions, true),
        item('策略摘要', plan.strategy_summary, true), item('风险提醒', plan.risk_reminders, true), item('缺失信息', plan.missing_information, true),
        item('生成模式', plan.generation_mode), item('模型名称', plan.model_name), item('fallback_used', plan.fallback_used),
        item('模型耗时', plan.model_duration_ms === null ? null : `${plan.model_duration_ms} ms`),
        item('Token 使用量', tokenStatistics(plan), true),
      ];
    }
    case 'resume_parser': {
      const profile = currentProfile.value;
      if (!profile) return [];
      return [
        item('技能', profile.skills, true), item('标准化技能', profile.normalized_skills, true), item('工作经验', profile.experience_months === null ? null : `${profile.experience_months} 个月`),
        item('教育经历', profile.education, true), item('项目', profile.projects, true), item('项目角色', profile.project_roles, true),
        item('项目技术', profile.project_technologies, true), item('可量化成果', profile.measurable_achievements, true), item('证书', profile.certificates, true),
        item('可到岗时间', profile.availability), item('缺失字段', profile.missing_fields, true), item('extraction_mode', profile.extraction_mode),
        item('fallback_used', profile.fallback_used), item('证据条目', profile.evidence_items, true),
      ];
    }
    case 'job_match': {
      const match = currentMatch.value;
      if (!match) return [];
      return [
        item('overall_score', match.overall_score), item('job_match_score', match.job_match_score), item('维度得分', match.dimension_scores, true),
        item('must_have_passed', match.must_have_passed), item('匹配技能', match.matched_skills, true), item('缺失技能', match.missing_skills, true),
        item('证据 ID', match.evidence_ids, true), item('建议面试问题', match.suggested_interview_questions, true),
        item('recommended_action', match.recommended_action), item('scoring_mode', match.scoring_mode), item('requires_review', match.requires_review),
      ];
    }
    case 'decision_review': {
      const review = currentReview.value;
      if (!review) return [];
      return [
        item('confidence', review.confidence), item('findings', review.findings, true), item('risk_tags', review.risk_tags, true),
        item('agent_disagreements', review.agent_disagreements, true), item('deterministic_score_preserved', review.deterministic_score_preserved),
        item('recommended_action', review.recommended_action), item('review_mode', review.review_mode),
      ];
    }
    case 'hr_report': {
      const report = snapshot.report;
      if (!report) return [];
      return [
        item('候选人排序', report.candidate_rankings.map((id) => candidateLabel(id, props.candidateNames)), true),
        item('候选人审查', report.candidate_reviews, true), item('执行摘要', report.executive_summary, true), item('人才缺口', report.talent_gaps, true),
        item('风险摘要', report.risk_summary, true), item('缺失信息', report.missing_information, true), item('下一步动作', report.next_actions, true),
        item('requires_human_decision', report.requires_human_decision), item('generation_mode', report.generation_mode), item('model_name', report.model_name),
        item('fallback_used', report.fallback_used), item('model_duration_ms', report.model_duration_ms), item('Token 使用量', tokenStatistics(report), true),
      ];
    }
    case 'interview_evaluation': {
      const evaluation = currentInterview.value;
      if (!evaluation) return [];
      return [
        item('status', evaluation.status), item('conclusion', evaluation.conclusion, true), item('strengths', evaluation.strengths, true),
        item('risks', evaluation.risks, true), item('evidence', evaluation.evidence, true), item('conflicts', evaluation.conflicts, true),
        item('requires_review', evaluation.requires_review),
      ];
    }
    default:
      return [];
  }
});

const outputEmptyMessage = computed(() => {
  if (!props.snapshot) return '当前尚未执行招聘工作流，没有本次运行结果。';
  if (status.value === AgentNodeStatus.WAITING) return '该 Agent 尚未执行，没有本次运行结果。';
  if (status.value === AgentNodeStatus.RUNNING) return '该 Agent 正在执行，结果将在真实事件到达后更新。';
  if (status.value === AgentNodeStatus.SKIPPED) return `该 Agent 已跳过，未生成处理结果。${skipReason.value ? ` 原因：${skipReason.value}` : ''}`;
  return '当前 Snapshot 中没有该 Agent 的结构化结果。';
});

const selectedCandidateLabel = computed(() => selectedCandidateId.value === null ? '—' : candidateLabel(selectedCandidateId.value, props.candidateNames));

watch(candidateIds, (ids) => {
  if (selectedCandidateId.value === null || !ids.includes(selectedCandidateId.value)) selectedCandidateId.value = ids[0] ?? null;
}, { immediate: true });

watch(() => props.open, async (isOpen) => {
  if (isOpen) {
    if (bodyOverflowBeforeDialog === null) {
      bodyOverflowBeforeDialog = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
    }
    window.addEventListener('keydown', handleKeydown);
    await nextTick();
    dialogRef.value?.focus();
  } else {
    releaseDialogEffects();
  }
}, { immediate: true });

onBeforeUnmount(releaseDialogEffects);

function releaseDialogEffects(): void {
  window.removeEventListener('keydown', handleKeydown);
  if (bodyOverflowBeforeDialog !== null) {
    document.body.style.overflow = bodyOverflowBeforeDialog;
    bodyOverflowBeforeDialog = null;
  }
}

function handleKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape' && props.open) emit('close');
}

function item(label: string, value: unknown, wide = false): DisplayItem {
  return { label, value, wide };
}

function summaryValue(key: string): unknown {
  for (let index = nodeEvents.value.length - 1; index >= 0; index -= 1) {
    const value = nodeEvents.value[index]?.summary[key];
    if (value !== undefined) return value;
  }
  return undefined;
}

function tokenStatistics(value: { prompt_tokens: number | null; completion_tokens: number | null; total_tokens: number | null }): Record<string, number | null> {
  return { prompt_tokens: value.prompt_tokens, completion_tokens: value.completion_tokens, total_tokens: value.total_tokens };
}

function displayValue(value: unknown): string {
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (Array.isArray(value)) return value.length ? value.map((entry) => typeof entry === 'object' ? JSON.stringify(entry) : String(entry)).join('、') : '—';
  if (value && typeof value === 'object') return JSON.stringify(value, null, 2);
  return value === null || value === undefined || value === '' ? '—' : String(value);
}

const SectionHeading = defineComponent({
  props: { title: { type: String, required: true }, icon: { type: Object as () => Component, required: true } },
  setup(componentProps) {
    return () => h('h3', { class: 'mb-3 flex items-center gap-2 text-base font-black text-slate-900' }, [
      h(componentProps.icon, { class: 'h-4 w-4 text-indigo-600', 'aria-hidden': 'true' }),
      componentProps.title,
    ]);
  },
});

const MetricCard = defineComponent({
  props: { label: { type: String, required: true }, value: { type: String, required: true }, wide: Boolean },
  setup(componentProps) {
    return () => h('div', { class: ['min-w-0 rounded-2xl border border-slate-200 bg-slate-50/70 p-3', componentProps.wide ? 'col-span-2 sm:col-span-3 lg:col-span-1' : ''] }, [
      h('p', { class: 'text-[11px] font-semibold text-slate-400' }, componentProps.label),
      h('p', { class: 'mt-1 truncate text-sm font-black text-slate-800', title: componentProps.value }, componentProps.value),
    ]);
  },
});

const DataCard = defineComponent({
  props: { label: { type: String, required: true }, value: { required: false }, wide: Boolean },
  setup(componentProps) {
    return () => {
      const value = displayValue(componentProps.value);
      const complex = Array.isArray(componentProps.value) && componentProps.value.some((entry) => typeof entry === 'object')
        || Boolean(componentProps.value && typeof componentProps.value === 'object' && !Array.isArray(componentProps.value));
      return h('article', { class: ['min-w-0 rounded-2xl border border-slate-200 bg-white p-4', componentProps.wide ? 'sm:col-span-2 lg:col-span-3' : ''] }, [
        h('p', { class: 'text-[11px] font-semibold text-slate-400' }, componentProps.label),
        complex
          ? h('details', { class: 'mt-2' }, [
              h('summary', { class: 'cursor-pointer text-xs font-semibold text-indigo-600' }, '查看结构化结果'),
              h('pre', { class: 'mt-3 max-h-72 overflow-auto whitespace-pre-wrap break-words rounded-xl bg-slate-50 p-3 font-mono text-[11px] leading-5 text-slate-600' }, value),
            ])
          : h('p', { class: 'mt-1 break-words whitespace-pre-wrap text-sm font-semibold leading-6 text-slate-700' }, value),
      ]);
    };
  },
});
</script>

<style scoped>
[data-theme="dark"] section[role="dialog"],
[data-theme="dark"] .bg-white,
[data-theme="dark"] .bg-white\/95 { background-color: #1e293b !important; }
[data-theme="dark"] .bg-slate-50,
[data-theme="dark"] .bg-slate-50\/70,
[data-theme="dark"] .bg-slate-50\/60,
[data-theme="dark"] .bg-slate-100 { background-color: #0f172a !important; }
[data-theme="dark"] .bg-indigo-50,
[data-theme="dark"] .bg-indigo-50\/70 { background-color: #1e1b4b !important; }
[data-theme="dark"] .bg-blue-50 { background-color: #172554 !important; }
[data-theme="dark"] .bg-emerald-50 { background-color: #052e16 !important; }
[data-theme="dark"] .bg-amber-50 { background-color: #451a03 !important; }
[data-theme="dark"] .bg-red-50 { background-color: #450a0a !important; }
[data-theme="dark"] .text-slate-900,
[data-theme="dark"] .text-slate-800 { color: #e2e8f0 !important; }
[data-theme="dark"] .text-slate-700,
[data-theme="dark"] .text-slate-600 { color: #cbd5e1 !important; }
[data-theme="dark"] .text-slate-500,
[data-theme="dark"] .text-slate-400 { color: #94a3b8 !important; }
[data-theme="dark"] .text-indigo-800,
[data-theme="dark"] .text-indigo-700,
[data-theme="dark"] .text-indigo-600 { color: #c7d2fe !important; }
[data-theme="dark"] .text-blue-800 { color: #bfdbfe !important; }
[data-theme="dark"] .text-emerald-800 { color: #a7f3d0 !important; }
[data-theme="dark"] .text-amber-800 { color: #fde68a !important; }
[data-theme="dark"] .text-red-800 { color: #fecaca !important; }
[data-theme="dark"] .border-slate-200,
[data-theme="dark"] .border-slate-300 { border-color: #475569 !important; }
[data-theme="dark"] .border-indigo-100 { border-color: #3730a3 !important; }
[data-theme="dark"] select { color-scheme: dark; }
</style>
