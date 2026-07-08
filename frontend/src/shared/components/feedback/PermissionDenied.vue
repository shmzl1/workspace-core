<template>
  <div class="perm-denied">
    <div class="perm-denied__icon">
      <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0110 0v4" />
        <circle cx="12" cy="16" r="1" />
      </svg>
    </div>
    <h3 class="perm-denied__title">{{ title }}</h3>
    <p v-if="description" class="perm-denied__desc">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    description?: string;
  }>(),
  {
    title: '权限不足',
    description: '你当前的角色无权访问该页面，如需协助请联系 HR 管理员。',
  }
);
</script>

<style scoped lang="scss">
.perm-denied {
  display: grid;
  place-items: center;
  gap: 12px;
  padding: 64px 24px;
  text-align: center;
}

.perm-denied__icon {
  color: #f0a040;
  margin-bottom: 6px;
}

.perm-denied__title {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-muted);
}

.perm-denied__desc {
  max-width: 380px;
  color: var(--color-subtle);
  font-size: 14px;
  line-height: 1.5;
}
</style>
