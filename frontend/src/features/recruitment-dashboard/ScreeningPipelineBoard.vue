<template>
  <article class="pipeline-card tf-card">
    <div class="pipeline-card__header">
      <div>
        <h2 class="tf-section-title">AI 筛选流水线</h2>
        <p class="tf-section-subtitle">候选人简历解析与匹配过程</p>
      </div>
      <span class="tf-tag">实时视图</span>
    </div>

    <div class="pipeline-card__board">
      <template v-for="(stage, index) in pipelineStages" :key="stage.title">
        <section class="pipeline-stage" :class="{ 'pipeline-stage--match': stage.match }">
          <div class="pipeline-stage__title">{{ stage.title }}</div>
          <div class="pipeline-stage__candidate">
            <strong>{{ stage.candidate }}</strong>
            <span>{{ stage.status }}</span>
          </div>
          <div v-if="stage.progress" class="pipeline-stage__progress">
            <i :style="{ width: `${stage.progress}%` }"></i>
          </div>
          <div v-if="stage.match" class="pipeline-stage__match">{{ stage.match }}</div>
          <div v-if="stage.tags" class="pipeline-stage__tags">
            <span v-for="tag in stage.tags" :key="tag">{{ tag }}</span>
          </div>
        </section>

        <div v-if="index < pipelineStages.length - 1" class="pipeline-card__connector">
          <span></span>
        </div>
      </template>
    </div>
  </article>
</template>

<script setup lang="ts">
import { pipelineStages } from '../../mock/recruitmentDashboard';
</script>

<style scoped lang="scss">
.pipeline-card {
  padding: 20px;
}

.pipeline-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.pipeline-card__board {
  display: grid;
  grid-template-columns: 1fr 56px 1fr 56px 1fr;
  align-items: center;
  min-height: 280px;
  margin-top: 20px;
  padding: 22px;
  border: 1px solid #dfebff;
  border-radius: var(--radius-md);
  background-image:
    linear-gradient(rgba(36, 85, 245, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(36, 85, 245, 0.06) 1px, transparent 1px);
  background-size: 24px 24px;
}

.pipeline-stage {
  min-height: 168px;
  padding: 18px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 28px rgba(36, 85, 245, 0.08);
  animation: floatStage 4s ease-in-out infinite;
}

.pipeline-stage:nth-child(3) {
  animation-delay: 0.45s;
}

.pipeline-stage:nth-child(5) {
  animation-delay: 0.8s;
}

.pipeline-stage--match {
  border-color: rgba(22, 163, 106, 0.42);
  box-shadow: 0 14px 34px rgba(22, 163, 106, 0.12);
}

.pipeline-stage__title {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 800;
}

.pipeline-stage__candidate {
  display: grid;
  margin-top: 18px;
  gap: 6px;
}

.pipeline-stage__candidate strong {
  font-size: 17px;
}

.pipeline-stage__candidate span {
  color: var(--color-muted);
  font-size: 13px;
}

.pipeline-stage__progress {
  height: 8px;
  margin-top: 18px;
  overflow: hidden;
  border-radius: 999px;
  background: #e6eeff;
}

.pipeline-stage__progress i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--color-primary);
}

.pipeline-stage__match {
  display: inline-flex;
  margin-top: 15px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(22, 163, 106, 0.12);
  color: var(--color-success);
  font-size: 13px;
  font-weight: 800;
}

.pipeline-stage__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.pipeline-stage__tags span {
  padding: 5px 8px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475467;
  font-size: 12px;
}

.pipeline-card__connector {
  display: flex;
  align-items: center;
  justify-content: center;
}

.pipeline-card__connector span {
  position: relative;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #b7c8ff, var(--color-primary));
}

.pipeline-card__connector span::after {
  position: absolute;
  top: -4px;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-primary);
  box-shadow: 0 0 0 6px rgba(36, 85, 245, 0.12);
  content: '';
}

@keyframes floatStage {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

@media (max-width: 760px) {
  .pipeline-card__board {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .pipeline-card__connector {
    height: 28px;
  }

  .pipeline-card__connector span {
    width: 2px;
    height: 100%;
  }
}
</style>
