  <template>
  <article
    class="matrix-card tf-card reveal-item"
    :style="{ animationDelay: `${(revealDelay ?? 0).toFixed(2)}s` }"
  >
    <div
      class="matrix-card__header reveal-item"
      :style="{ animationDelay: `${((revealDelay ?? 0) + 0.15).toFixed(2)}s` }"
    >
      <div>
        <h2 class="tf-section-title">招聘热度矩阵</h2>
        <p class="tf-section-subtitle">AI 预测未来 7 天的招聘活跃度</p>
      </div>
      <div class="matrix-card__legend">
        <span>低热度</span>
        <i class="matrix-card__legend-bar"></i>
        <span>高热度</span>
      </div>
    </div>

    <div
      class="matrix-card__content reveal-item"
      :style="{ animationDelay: `${((revealDelay ?? 0) + 0.3).toFixed(2)}s` }"
    >
      <div class="matrix-card__days">
        <span v-for="day in heatmapRows" :key="day">{{ day }}</span>
      </div>
      <div class="matrix-card__grid">
        <span
          v-for="(value, index) in values"
          :key="index"
          class="matrix-card__cell"
          :class="`matrix-card__cell--${value}`"
        ></span>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
const props = defineProps<{ values: number[]; revealDelay?: number }>();
const values = props.values;
const heatmapRows = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
</script>

<style scoped lang="scss">
.matrix-card {
  padding: 20px;
}

.matrix-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.matrix-card__legend {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-muted);
  font-size: 12px;
  white-space: nowrap;
}

.matrix-card__legend-bar {
  width: 62px;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(90deg, #eaf1ff, #2455f5);
}

.matrix-card__content {
  display: grid;
  grid-template-columns: 46px 1fr;
  gap: 12px;
  margin-top: 22px;
}

.matrix-card__days {
  display: grid;
  grid-template-rows: repeat(7, 18px);
  gap: 7px;
  color: var(--color-muted);
  font-size: 12px;
}

.matrix-card__days span {
  display: flex;
  align-items: center;
}

.matrix-card__grid {
  display: grid;
  grid-template-columns: repeat(18, minmax(13px, 1fr));
  gap: 7px;
  min-width: 0;
}

.matrix-card__cell {
  height: 18px;
  border-radius: 5px;
}

.matrix-card__cell--1 {
  background: #edf3ff;
}

.matrix-card__cell--2 {
  background: #cfe0ff;
}

.matrix-card__cell--3 {
  background: #9ebcff;
}

.matrix-card__cell--4 {
  background: #5f88ff;
}

.matrix-card__cell--5 {
  background: #2455f5;
}

/* 深色模式适配 */
[data-theme="dark"] .matrix-card__cell--1 { background: #1e3a5f; }
[data-theme="dark"] .matrix-card__cell--2 { background: #1e40af; }

@media (max-width: 720px) {
  .matrix-card__header {
    flex-direction: column;
  }

  .matrix-card__grid {
    grid-template-columns: repeat(9, minmax(13px, 1fr));
  }
}
</style>
