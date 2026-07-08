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
      <ScreeningPipelineBoard class="dashboard-page__pipeline" />
      <WeeklyScheduleCard />
    </div>

    <div class="dashboard-page__lower">
      <HiringIntensityMatrix />
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
        <article v-for="item in payrollReviewItems" :key="item.employee" class="payroll-risk__item">
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
import KpiCard from '../../../shared/components/base/KpiCard.vue';
import AgentTraceCard from './AgentTraceCard.vue';
import HiringIntensityMatrix from './HiringIntensityMatrix.vue';
import ScreeningPipelineBoard from './ScreeningPipelineBoard.vue';
import WeeklyScheduleCard from './WeeklyScheduleCard.vue';
import { kpiItems } from '../../../shared/data/recruitmentDashboard';

const payrollReviewItems = [
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
];

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
  background: #fff;
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
