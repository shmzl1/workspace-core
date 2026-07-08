<template>
  <div class="error-state">
    <div class="error-state__icon">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="13" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
    </div>
    <h3 class="error-state__title">{{ title }}</h3>
    <p v-if="message" class="error-state__message">{{ message }}</p>
    <button v-if="retryLabel" class="error-state__retry" @click="$emit('retry')">
      {{ retryLabel }}
    </button>
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    message?: string;
    retryLabel?: string;
  }>(),
  { title: '加载失败', message: '', retryLabel: '' }
);

defineEmits<{
  retry: [];
}>();
</script>

<style scoped lang="scss">
.error-state {
  display: grid;
  place-items: center;
  gap: 12px;
  padding: 60px 24px;
  text-align: center;
}

.error-state__icon {
  color: #e55c3c;
  margin-bottom: 6px;
}

.error-state__title {
  font-size: 18px;
  font-weight: 800;
  color: var(--color-muted);
}

.error-state__message {
  max-width: 400px;
  color: var(--color-subtle);
  font-size: 14px;
  line-height: 1.5;
}

.error-state__retry {
  margin-top: 8px;
  padding: 10px 26px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}
</style>
