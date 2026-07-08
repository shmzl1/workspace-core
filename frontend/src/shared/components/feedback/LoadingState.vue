<template>
  <div class="loading-state">
    <div class="loading-state__spinner">
      <span class="loading-state__ring"></span>
    </div>
    <p class="loading-state__text">{{ message }}</p>
    <small v-if="detail" class="loading-state__detail">{{ detail }}</small>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    message?: string;
    detail?: string;
  }>(),
  { message: '加载中…', detail: '' }
);
</script>

<style scoped lang="scss">
.loading-state {
  display: grid;
  place-items: center;
  gap: 18px;
  padding: 64px 24px;
  color: var(--color-muted);
  text-align: center;
}

.loading-state__spinner {
  display: grid;
  place-items: center;
}

.loading-state__ring {
  width: 42px;
  height: 42px;
  border: 3px solid var(--color-line);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-state__text {
  font-size: 16px;
  font-weight: 700;
}

.loading-state__detail {
  margin-top: -6px;
  color: var(--color-subtle);
  font-size: 13px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
