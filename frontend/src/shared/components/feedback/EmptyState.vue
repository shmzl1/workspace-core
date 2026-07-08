<template>
  <div class="empty-state">
    <div class="empty-state__icon">
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
      </svg>
    </div>
    <h3 class="empty-state__title">{{ title }}</h3>
    <p v-if="description" class="empty-state__desc">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    description?: string;
  }>(),
  { title: '暂无数据', description: '' }
);
</script>

<style scoped lang="scss">
.empty-state {
  display: grid;
  place-items: center;
  gap: 12px;
  padding: 60px 24px;
  color: var(--color-muted);
  text-align: center;
}

.empty-state__icon {
  color: var(--color-subtle);
  margin-bottom: 6px;
}

.empty-state__title {
  font-size: 18px;
  font-weight: 800;
  color: var(--color-muted);
}

.empty-state__desc {
  max-width: 360px;
  color: var(--color-subtle);
  font-size: 14px;
  line-height: 1.5;
}
</style>
