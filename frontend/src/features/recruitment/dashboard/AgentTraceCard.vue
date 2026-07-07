<template>
  <article class="trace-card">
    <div class="trace-card__header">
      <div>
        <h2 class="tf-section-title">LangGraph 执行记录</h2>
        <p class="tf-section-subtitle">前端模拟链路事件</p>
      </div>
      <span>实时</span>
    </div>

    <div class="trace-card__nodes">
      <span>Input</span>
      <i></i>
      <span>Tool</span>
      <i></i>
      <span>LLM</span>
    </div>

    <ul class="trace-card__logs">
      <li v-for="log in logs" :key="log">
        <span></span>
        {{ log }}
      </li>
    </ul>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  logs: string[];
}>();
</script>

<style scoped lang="scss">
.trace-card {
  min-height: 300px;
  padding: 20px;
  border-radius: var(--radius-lg);
  background: linear-gradient(150deg, #111827, #0b1120);
  box-shadow: 0 18px 44px rgba(16, 24, 40, 0.22);
  color: #fff;
}

.trace-card__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.trace-card__header .tf-section-title {
  color: #fff;
}

.trace-card__header .tf-section-subtitle {
  color: #98a2b3;
}

.trace-card__header > span {
  height: 26px;
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(22, 163, 106, 0.16);
  color: #7ee0b2;
  font-size: 12px;
  font-weight: 800;
}

.trace-card__nodes {
  display: flex;
  align-items: center;
  margin-top: 24px;
  gap: 10px;
}

.trace-card__nodes span {
  display: grid;
  min-width: 58px;
  min-height: 34px;
  place-items: center;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.06);
  color: #dbe7ff;
  font-size: 12px;
  font-weight: 800;
}

.trace-card__nodes i {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, rgba(36, 85, 245, 0.2), #5b7cff);
}

.trace-card__logs {
  display: grid;
  margin: 24px 0 0;
  padding: 0;
  gap: 10px;
  list-style: none;
}

.trace-card__logs li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.5;
}

.trace-card__logs span {
  width: 7px;
  height: 7px;
  margin-top: 7px;
  border-radius: 50%;
  background: #7aa2ff;
  box-shadow: 0 0 12px #7aa2ff;
}
</style>
