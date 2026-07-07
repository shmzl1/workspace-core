<template>
  <header class="bg-surface/80 backdrop-blur-md border-b border-outline-variant sticky top-0 z-40 flex justify-between items-center w-full px-8 py-3">
    <div class="flex items-center gap-8">
      <div class="font-bold text-xl text-primary md:hidden">TalentOS AI</div>
      
      <!-- Search -->
      <div class="hidden md:flex relative group">
        <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline group-focus-within:text-primary transition-colors">search</span>
        <input 
          type="text" 
          placeholder="提问 AI 或搜索..." 
          class="pl-10 pr-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-full text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-64 md:w-80 transition-all"
        />
        <div class="absolute right-2 top-1/2 -translate-y-1/2 flex items-center justify-center w-6 h-6 rounded bg-primary/10 text-primary text-[10px] font-mono">⌘K</div>
      </div>
    </div>

    <div class="flex items-center gap-4">
      <button 
        @click="$emit('toggleRole')"
        class="text-xs font-medium border border-outline-variant rounded-full px-3 py-1 hover:bg-surface-container-low transition-colors text-on-surface-variant hover:text-primary flex items-center gap-1"
      >
        <span class="material-symbols-outlined text-[14px]">swap_horiz</span>
        切至 {{ role === 'hr' ? '员工端' : 'HR端' }}
      </button>
      <button class="text-on-surface-variant hover:text-primary transition-all p-2 rounded-full hover:bg-surface-container-low relative">
        <span class="material-symbols-outlined">notifications</span>
        <span class="absolute top-2 right-2 w-2 h-2 rounded-full bg-error border-2 border-surface"></span>
      </button>
      <button class="hidden sm:block text-on-surface-variant hover:text-primary transition-all p-2 rounded-full hover:bg-surface-container-low">
        <span class="material-symbols-outlined">history</span>
      </button>
      <button class="hidden sm:block text-on-surface-variant hover:text-primary transition-all p-2 rounded-full hover:bg-surface-container-low">
        <span class="material-symbols-outlined">dark_mode</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import type { ViewType, Role } from '../types';

defineProps<{
  role: Role;
  currentView: ViewType;
}>();

defineEmits<{
  (e: 'toggleRole'): void;
  (e: 'navigate', view: ViewType): void;
}>();
</script>
