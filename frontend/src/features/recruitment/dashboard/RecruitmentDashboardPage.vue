<template>
  <section class="dashboard-page">
    <div class="dashboard-page__header">
      <div>
        <p class="dashboard-page__eyebrow">企业级 HR 智能助手概览</p>
        <h1>{{ pageTitle }}</h1>
      </div>
      <button class="dashboard-page__export" type="button" @click="$emit('exportReport')">
        <span></span>
        导出报告
      </button>
    </div>

    <div class="dashboard-page__kpis">
      <KpiCard v-for="item in kpiItems" :key="item.id" :item="item" />
    </div>

    <div class="dashboard-page__grid">
      <ScreeningPipelineBoard class="dashboard-page__pipeline" :pipeline-stages="pipelineStages" />
      <WeeklyScheduleCard :weekly-schedule="weeklySchedule" />
    </div>

    <div class="dashboard-page__lower">
      <HiringIntensityMatrix :values="heatmapValues" />
      <AgentTraceCard :logs="traceLogs" />
    </div>

    <section class="payroll-risk">
      <div class="payroll-risk__header">
        <div>
          <p class="dashboard-page__eyebrow">薪资预审与风险提示</p>
          <h2>待处理薪资预审</h2>
        </div>
        <button type="button">查看全部</button>
      </div>

      <div class="payroll-risk__grid">
        <article v-for="item in payrollReviewItems" :key="item.id" class="payroll-risk__item">
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
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
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
const heatmapValues = computed(() => Array.from({ length: 126 }, (_, index) => {
  const item = applications.value[index % Math.max(applications.value.length, 1)];
  return item?.score_total ? Math.min(5, Math.max(1, Math.ceil(Number(item.score_total) / 20))) : 1;
}));

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
