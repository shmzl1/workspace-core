<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between gap-3">
      <p class="text-xs font-semibold text-on-surface-variant">空闲时间（每段至少 {{ minimumMinutes }} 分钟）</p>
      <button
        type="button"
        class="flex items-center gap-1 text-xs font-semibold text-primary hover:underline disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="disabled"
        @click="$emit('add')"
      >
        <span class="material-symbols-outlined text-[16px]">add</span>
        添加时间段
      </button>
    </div>

    <div v-for="(slot, index) in slots" :key="index" class="grid grid-cols-[1fr_auto] gap-2 rounded-lg bg-surface-container-low p-2">
      <div class="grid grid-cols-1 gap-2">
        <label class="space-y-1">
          <span class="block text-[11px] text-on-surface-variant">开始时间</span>
          <input
            v-model="slot.start"
            type="datetime-local"
            :disabled="disabled"
            class="w-full rounded-md border border-outline-variant bg-surface-container-lowest px-2 py-1.5 text-xs text-on-surface outline-none focus:border-primary disabled:cursor-not-allowed disabled:opacity-60"
          >
        </label>
        <label class="space-y-1">
          <span class="block text-[11px] text-on-surface-variant">结束时间</span>
          <input
            v-model="slot.end"
            type="datetime-local"
            :disabled="disabled"
            class="w-full rounded-md border border-outline-variant bg-surface-container-lowest px-2 py-1.5 text-xs text-on-surface outline-none focus:border-primary disabled:cursor-not-allowed disabled:opacity-60"
          >
        </label>
      </div>
      <button
        type="button"
        class="self-center rounded-md p-1.5 text-on-surface-variant hover:bg-red-50 hover:text-red-800 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="disabled"
        aria-label="删除时间段"
        @click="$emit('remove', index)"
      >
        <span class="material-symbols-outlined text-[18px]">delete</span>
      </button>
    </div>

    <p v-if="error" class="flex items-start gap-1 text-xs leading-5 text-red-800">
      <span class="material-symbols-outlined mt-0.5 text-[15px]">error</span>
      {{ error }}
    </p>
  </div>
</template>

<script setup lang="ts">
type AvailabilitySlotDraft = {
  start: string;
  end: string;
};

defineProps<{
  slots: AvailabilitySlotDraft[];
  disabled: boolean;
  minimumMinutes: number;
  error?: string;
}>();

defineEmits<{
  add: [];
  remove: [index: number];
}>();
</script>
