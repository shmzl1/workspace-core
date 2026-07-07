<template>
  <section class="dashboard-page">
    <div class="dashboard-page__header">
      <div>
        <p class="dashboard-page__eyebrow">企业级 HR AI 助手概览</p>
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
  </section>
</template>

<script setup lang="ts">
import KpiCard from '../../../shared/components/base/KpiCard.vue';
import AgentTraceCard from './AgentTraceCard.vue';
import HiringIntensityMatrix from './HiringIntensityMatrix.vue';
import ScreeningPipelineBoard from './ScreeningPipelineBoard.vue';
import WeeklyScheduleCard from './WeeklyScheduleCard.vue';
import { kpiItems } from '../../../mock/recruitmentDashboard';

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

@media (max-width: 1180px) {
  .dashboard-page__kpis {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-page__grid,
  .dashboard-page__lower {
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
