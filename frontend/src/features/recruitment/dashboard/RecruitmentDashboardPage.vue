<template>
  <section class="dashboard-page">
    <div class="dashboard-page__header">
      <div>
        <p class="dashboard-page__eyebrow reveal-item" style="animation-delay: 0.00s">企业级 HR 智能助手概览</p>
        <h1 class="reveal-item" style="animation-delay: 0.15s">{{ pageTitle }}</h1>
      </div>
      <button
        class="dashboard-page__export reveal-item"
        style="animation-delay: 0.30s"
        type="button"
        @click="$emit('exportReport')"
      >
        <span></span>
        导出报告
      </button>
    </div>

    <div class="dashboard-page__kpis">
      <KpiCard
        v-for="(item, idx) in kpiItems"
        :key="item.id"
        :item="item"
        :reveal-delay="(3 + idx) * 0.15"
      />
    </div>

    <div class="dashboard-page__grid">
      <ScreeningPipelineBoard
        class="dashboard-page__pipeline"
        :pipeline-stages="pipelineStages"
        :reveal-delay="7 * 0.15"
      />
      <WeeklyScheduleCard
        :weekly-schedule="weeklySchedule"
        :reveal-delay="16 * 0.15"
      />
    </div>

    <div class="dashboard-page__lower">
      <HiringIntensityMatrix
        :values="heatmapValues"
        :reveal-delay="18 * 0.15"
      />
      <AgentTraceCard
        :logs="traceLogs"
        :reveal-delay="20 * 0.15"
      />
    </div>

    <section class="payroll-risk dashboard-hover-card">
      <div class="payroll-risk__header">
        <div>
          <p class="dashboard-page__eyebrow reveal-item" style="animation-delay: 3.30s">薪资预审与风险提示</p>
          <h2 class="reveal-item" style="animation-delay: 3.45s">待处理薪资预审</h2>
        </div>
        <button class="reveal-item" style="animation-delay: 3.60s" type="button">查看全部</button>
      </div>

      <div class="payroll-risk__grid">
        <div
          v-for="(item, idx) in payrollReviewItems"
          :key="item.id"
          class="dashboard-card-reveal reveal-item"
          :style="{ animationDelay: `${(3.75 + idx * 0.15).toFixed(2)}s` }"
        >
          <article class="payroll-risk__item dashboard-hover-card--compact">
          <div class="payroll-risk__item-head">
            <strong>{{ item.employee }}</strong>
            <span>{{ item.status }}</span>
          </div>
          <dl>
            <div>
              <dt>薪资周期</dt>
              <dd>{{ item.period }}</dd>
            </div>
            <div>
              <dt>预览实发</dt>
              <dd>{{ item.net }}</dd>
            </div>
            <div>
              <dt>异常提示</dt>
              <dd>{{ item.risk }}</dd>
            </div>
          </dl>
          <p>{{ item.suggestion }}</p>
          </article>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import '../../../shared/styles/reveal-animations.css';
import KpiCard from '../../../shared/components/base/KpiCard.vue';
import AgentTraceCard from './AgentTraceCard.vue';
import HiringIntensityMatrix from './HiringIntensityMatrix.vue';
import ScreeningPipelineBoard from './ScreeningPipelineBoard.vue';
import WeeklyScheduleCard from './WeeklyScheduleCard.vue';
import { fetchApplications } from '../../../shared/api/modules/recruitment';
import { fetchInterviews } from '../../../shared/api/modules/interview';
import { fetchPayrollReviewRecords, type PayrollReviewSummary } from '../../../shared/api/modules/payrollReview';
import apiClient from '../../../shared/api/apiClient';
import type { KpiItem, PipelineStage } from '../../../shared/types/recruitmentDashboard';

const dashboard = ref({ jobs_count: 0, candidates_count: 0, applications_count: 0, pending_score_count: 0 });
const applications = ref<Awaited<ReturnType<typeof fetchApplications>>>([]);
const interviews = ref<Awaited<ReturnType<typeof fetchInterviews>>>([]);
const payrollReviews = ref<PayrollReviewSummary[]>([]);
type HeatmapLevel = 1 | 2 | 3 | 4 | 5;

const demoHeatmapRows: HeatmapLevel[][] = [
  [1, 1, 2, 2, 3, 3, 2, 3, 4, 4, 5, 4, 3, 4, 5, 4, 3, 2],
  [1, 2, 2, 3, 3, 4, 3, 4, 4, 5, 4, 5, 4, 3, 4, 4, 3, 2],
  [1, 2, 3, 3, 4, 4, 3, 4, 5, 5, 4, 4, 5, 4, 4, 3, 2, 2],
  [1, 2, 2, 3, 4, 3, 3, 4, 4, 5, 5, 4, 4, 4, 3, 3, 2, 1],
  [1, 1, 2, 3, 3, 4, 3, 4, 5, 4, 4, 5, 4, 3, 3, 2, 2, 1],
  [1, 1, 1, 2, 2, 2, 1, 2, 3, 2, 3, 2, 2, 2, 1, 2, 1, 1],
  [1, 1, 2, 1, 2, 2, 1, 2, 2, 3, 2, 2, 3, 2, 2, 1, 1, 1],
];
const demoHeatmapValues = demoHeatmapRows.flat();

function toHeatmapLevel(score: number): HeatmapLevel {
  return Math.min(5, Math.max(1, Math.ceil(score / 20))) as HeatmapLevel;
}

const kpiItems = computed<KpiItem[]>(() => [
  { id: 'resumes', label: '新增简历', value: String(dashboard.value.applications_count), trend: '数据库实时', variant: 'plain' },
  { id: 'screened', label: 'AI 筛选完成', value: String(Math.max(0, dashboard.value.applications_count - dashboard.value.pending_score_count)), trend: '已评分', variant: 'gradient' },
  { id: 'interviews', label: '进入面试阶段', value: String(applications.value.filter((item) => ['INTERVIEW_PENDING', 'INTERVIEWING'].includes(item.current_stage)).length), variant: 'bars' },
  { id: 'graph', label: '智能分析链路', value: '实时', variant: 'dark' },
]);
const pipelineStages = computed<PipelineStage[]>(() => applications.value.slice(0, 3).map((item, index) => ({
  title: ['原始提取', '语义匹配', '优先候选'][index] ?? '候选人',
  candidate: item.candidate_name || `候选人 #${item.candidate_id}`,
  status: item.current_stage,
  progress: item.score_total === null ? undefined : Number(item.score_total),
  match: item.score_total === null ? undefined : `${item.score_total}% 匹配`,
})).concat(applications.value.length ? [] : [{ title: '暂无候选人', candidate: '等待数据', status: 'APPLIED', progress: undefined, match: undefined }]));
const weeklySchedule = computed(() => interviews.value.filter((item) => item.status === 'SCHEDULED').slice(0, 5).map((item) => {
  const start = new Date(item.start_at);
  const application = applications.value.find((row) => row.id === item.application_id);
  return { day: new Intl.DateTimeFormat('zh-CN', { weekday: 'short' }).format(start), date: String(start.getDate()), name: application?.candidate_name || `候选人 #${item.application_id}`, role: application?.job_title || '待确认岗位', time: start.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) };
}));
const heatmapValues = computed<HeatmapLevel[]>(() => {
  const validScores = applications.value
    .map((item) => item.score_total)
    .filter((score): score is number => score !== null && Number.isFinite(score));

  if (validScores.length < 3) return demoHeatmapValues;

  return Array.from({ length: 126 }, (_, index) => (
    toHeatmapLevel(validScores[index % validScores.length])
  ));
});

const payrollReviewItems = computed(() => payrollReviews.value
  .filter((item) => item.status !== 'CONFIRMED')
  .slice(0, 4)
  .map((item) => ({
    id: item.id,
    employee: item.employee_name || `员工 #${item.employee_id}`,
    period: item.period_code || '--',
    net: Number(item.net_salary_preview).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
    status: item.status,
    risk: item.status === 'PENDING_HR_CONFIRMATION' ? '等待 HR 复核' : '预审记录待处理',
    suggestion: '请在薪资预审明细中核对数据来源和审批状态。',
  })));

onMounted(async () => {
  const [dashboardData, applicationData, interviewData, payrollData] = await Promise.all([
    apiClient.get<typeof dashboard.value>('/recruitment/dashboard').then((response) => response.data),
    fetchApplications(),
    fetchInterviews(),
    fetchPayrollReviewRecords().catch(() => ({ records: [] })),
  ]);
  dashboard.value = dashboardData;
  applications.value = applicationData;
  interviews.value = interviewData;
  payrollReviews.value = payrollData.records;
});

/* Removed legacy mock payroll cards; the computed payrollReviewItems above is API-backed.
  {
    employee: '张伟',
    period: '2026-07',
    net: '12,420.00',
    status: '待 HR 确认',
    risk: '迟到扣款高于部门均值',
    suggestion: '建议核对考勤来源与扣款规则后再确认'
  },
  {
    employee: '刘敏',
    period: '2026-07',
    net: '14,860.00',
    status: '需复核',
    risk: '补贴录入与上月差异较大',
    suggestion: '建议复查交通补贴与餐补调整依据'
  }
]; */

defineProps<{
  pageTitle: string;
  traceLogs: string[];
}>();

defineEmits<{
  exportReport: [];
}>();
</script>

<style scoped lang="scss">
.dashboard-page {
  display: grid;
  max-width: 1240px;
  margin: 0 auto;
  gap: 22px;
}

.dashboard-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.dashboard-page__eyebrow {
  margin: 0 0 8px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 800;
}

.dashboard-page__header h1 {
  margin: 0;
  color: var(--color-text);
  font-size: 30px;
  letter-spacing: 0;
}

.dashboard-page__export {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: #fff;
  box-shadow: var(--shadow-soft);
  font-weight: 800;
}

.dashboard-page__export span {
  width: 14px;
  height: 14px;
  border: 2px solid #fff;
  border-top: 0;
  border-radius: 2px;
}

.dashboard-page__export span::before {
  display: block;
  width: 7px;
  height: 7px;
  margin: -8px 0 0 2px;
  border-right: 2px solid #fff;
  border-bottom: 2px solid #fff;
  transform: rotate(45deg);
  content: '';
}

.dashboard-page__kpis {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.dashboard-page__grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.85fr);
  gap: 18px;
}

.dashboard-page__lower {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
  gap: 18px;
}

.payroll-risk {
  display: grid;
  gap: 16px;
  padding: 18px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
}

.payroll-risk__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.payroll-risk__header h2 {
  margin: 0;
  color: var(--color-text);
  font-size: 22px;
  letter-spacing: 0;
}

.payroll-risk__header button {
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-weight: 800;
}

.payroll-risk__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.payroll-risk__item {
  display: grid;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: var(--color-surface-soft);
}

.payroll-risk__item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.payroll-risk__item-head span {
  padding: 5px 9px;
  border-radius: 999px;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 800;
}

.payroll-risk dl {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin: 0;
}

.payroll-risk dt {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 800;
}

.payroll-risk dd {
  margin: 5px 0 0;
  color: var(--color-text);
  font-weight: 800;
}

.payroll-risk__item p {
  margin: 0;
  color: var(--color-muted);
  line-height: 1.6;
}

@media (max-width: 1180px) {
  .dashboard-page__kpis {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-page__grid,
  .dashboard-page__lower,
  .payroll-risk__grid {
    grid-template-columns: 1fr;
  }

  .payroll-risk dl {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .dashboard-page__header {
    align-items: flex-start;
    flex-direction: column;
  }

  .dashboard-page__kpis {
    grid-template-columns: 1fr;
  }
}
</style>
