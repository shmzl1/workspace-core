<template>
  <article class="schedule-card tf-card">
    <div class="schedule-card__header">
      <h2 class="tf-section-title">每周日程</h2>
      <button aria-label="更多操作">
        <span></span><span></span><span></span>
      </button>
    </div>

    <div class="schedule-card__list">
      <section v-for="item in weeklySchedule" :key="item.name" class="schedule-item">
        <div class="schedule-item__date">
          <span>{{ item.day }}</span>
          <strong>{{ item.date }}</strong>
        </div>
        <div class="schedule-item__content">
          <strong>{{ item.name }}</strong>
          <span>{{ item.role }}</span>
          <time>{{ item.time }}</time>
        </div>
      </section>
    </div>
  </article>
</template>

<script setup lang="ts">
import { weeklySchedule } from '../../mock/recruitmentDashboard';
</script>

<style scoped lang="scss">
.schedule-card {
  padding: 20px;
}

.schedule-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.schedule-card__header button {
  display: flex;
  width: 32px;
  height: 32px;
  align-items: center;
  justify-content: center;
  gap: 3px;
  border-radius: 50%;
  background: var(--color-surface-soft);
}

.schedule-card__header button span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--color-muted);
}

.schedule-card__list {
  display: grid;
  margin-top: 18px;
  gap: 12px;
}

.schedule-item {
  display: flex;
  gap: 14px;
  padding: 14px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: #fff;
}

.schedule-item__date {
  display: grid;
  width: 58px;
  min-width: 58px;
  place-items: center;
  border-radius: var(--radius-sm);
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.schedule-item__date span {
  font-size: 12px;
  font-weight: 700;
}

.schedule-item__date strong {
  font-size: 22px;
}

.schedule-item__content {
  display: grid;
  min-width: 0;
  gap: 4px;
}

.schedule-item__content strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.schedule-item__content span,
.schedule-item__content time {
  color: var(--color-muted);
  font-size: 13px;
}
</style>
