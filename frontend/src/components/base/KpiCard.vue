<template>
  <article class="kpi-card" :class="`kpi-card--${item.variant}`">
    <template v-if="item.variant !== 'dark'">
      <div class="kpi-card__top">
        <span class="kpi-card__icon">
          <span v-if="item.variant === 'plain'" class="icon-doc"></span>
          <span v-else-if="item.variant === 'bars'" class="icon-funnel"></span>
          <span v-else class="icon-circle"></span>
        </span>
        <span v-if="item.trend" class="kpi-card__trend">{{ item.trend }}</span>
      </div>
      <div class="kpi-card__value">{{ item.value }}</div>
      <div class="kpi-card__label">{{ item.label }}</div>
      <svg v-if="item.variant === 'plain'" class="kpi-card__sparkline" viewBox="0 0 120 34">
        <path d="M4 26 L28 20 L48 22 L72 10 L94 14 L116 5" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
      </svg>
      <div v-if="item.variant === 'gradient'" class="kpi-card__progress">
        <span>75%</span>
        <i></i>
      </div>
      <div v-if="item.variant === 'bars'" class="kpi-card__bars">
        <span style="height: 38%"></span>
        <span style="height: 74%"></span>
        <span style="height: 52%"></span>
        <span style="height: 88%"></span>
      </div>
    </template>

    <template v-else>
      <div class="kpi-card__dark-head">
        <span>{{ item.label }}</span>
        <b>{{ item.value }}</b>
      </div>
      <div class="kpi-card__metric">
        <span>向量数据库</span>
        <strong>4.2ms</strong>
      </div>
      <div class="kpi-card__metric">
        <span>LLM 节点</span>
        <strong>2.8s</strong>
      </div>
      <p>正在查询候选人 “React.js” 相关技能知识图谱...</p>
    </template>
  </article>
</template>

<script setup lang="ts">
import type { KpiItem } from '../../mock/recruitmentDashboard';

defineProps<{
  item: KpiItem;
}>();
</script>

<style scoped lang="scss">
.kpi-card {
  position: relative;
  min-height: 176px;
  padding: 20px;
  overflow: hidden;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-lg);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.kpi-card__top,
.kpi-card__dark-head,
.kpi-card__metric {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kpi-card__icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 13px;
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.icon-doc {
  width: 17px;
  height: 21px;
  border: 2px solid currentColor;
  border-radius: 4px;
}

.icon-doc::after {
  display: block;
  width: 9px;
  height: 2px;
  margin: 7px 0 0 3px;
  background: currentColor;
  box-shadow: 0 5px 0 currentColor;
  content: '';
}

.icon-funnel {
  width: 18px;
  height: 18px;
  clip-path: polygon(0 0, 100% 0, 62% 48%, 62% 100%, 38% 100%, 38% 48%);
  background: currentColor;
}

.icon-circle {
  width: 22px;
  height: 22px;
  border: 5px solid rgba(255, 255, 255, 0.55);
  border-top-color: #fff;
  border-radius: 50%;
}

.kpi-card__trend {
  color: var(--color-success);
  font-size: 13px;
  font-weight: 800;
}

.kpi-card__value {
  margin-top: 18px;
  font-size: 36px;
  font-weight: 850;
}

.kpi-card__label {
  margin-top: 3px;
  color: var(--color-muted);
  font-size: 14px;
}

.kpi-card__sparkline {
  position: absolute;
  right: 18px;
  bottom: 16px;
  width: 118px;
  color: var(--color-primary);
  opacity: 0.75;
}

.kpi-card--gradient {
  background: linear-gradient(135deg, #2455f5, #6d57f5);
  color: #fff;
}

.kpi-card--gradient .kpi-card__label,
.kpi-card--gradient .kpi-card__trend {
  color: rgba(255, 255, 255, 0.8);
}

.kpi-card--gradient .kpi-card__icon {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}

.kpi-card__progress {
  position: absolute;
  right: 20px;
  bottom: 18px;
  display: grid;
  width: 64px;
  height: 64px;
  place-items: center;
  border-radius: 50%;
  background: conic-gradient(#fff 75%, rgba(255, 255, 255, 0.22) 0);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
}

.kpi-card__progress i {
  position: absolute;
  inset: 8px;
  border-radius: 50%;
  background: #435ff8;
}

.kpi-card__progress span {
  position: relative;
  z-index: 1;
}

.kpi-card__bars {
  position: absolute;
  right: 22px;
  bottom: 20px;
  display: flex;
  align-items: end;
  width: 86px;
  height: 52px;
  gap: 8px;
}

.kpi-card__bars span {
  flex: 1;
  border-radius: 999px 999px 4px 4px;
  background: linear-gradient(180deg, #2455f5, #c7d6ff);
}

.kpi-card--dark {
  border-color: #1d2939;
  background: linear-gradient(145deg, #111827, #0b1220);
  color: #fff;
}

.kpi-card__dark-head span {
  font-weight: 800;
}

.kpi-card__dark-head b {
  padding: 4px 9px;
  border-radius: 999px;
  background: rgba(36, 85, 245, 0.26);
  color: #9bb7ff;
  font-size: 12px;
}

.kpi-card__metric {
  margin-top: 15px;
  color: #cbd5e1;
  font-size: 13px;
}

.kpi-card__metric strong {
  color: #fff;
}

.kpi-card--dark p {
  margin: 18px 0 0;
  color: #a8b3c7;
  font-size: 12px;
  line-height: 1.6;
}
</style>
