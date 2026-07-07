<template>
  <Transition name="toast">
    <div v-if="message" class="toast-message">
      {{ message }}
    </div>
  </Transition>
</template>

<script setup lang="ts">
defineProps<{
  message: string;
}>();
</script>

<style scoped lang="scss">
.toast-message {
  position: fixed;
  right: 32px;
  bottom: 150px;
  z-index: 40;
  max-width: min(420px, calc(100vw - 40px));
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  background: rgba(16, 24, 40, 0.92);
  color: #fff;
  box-shadow: 0 18px 42px rgba(16, 24, 40, 0.24);
  font-size: 14px;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}

.toast-enter-from,
.toast-leave-to {
  transform: translateY(10px);
  opacity: 0;
}
</style>
