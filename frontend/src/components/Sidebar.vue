<template>
  <nav class="h-screen w-[256px] fixed left-0 top-0 bg-surface-container-lowest border-r border-outline-variant/30 shadow-sm flex flex-col py-8 px-4 z-50 overflow-y-auto">
    <div 
      class="mb-8 px-2 cursor-pointer flex items-center gap-3"
      @click="$emit('navigate', 'welcome')"
    >
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-tertiary flex items-center justify-center text-on-primary shadow-lg shadow-primary/20">
        <span class="material-symbols-outlined">{{ role === 'hr' ? 'psychology' : 'work' }}</span>
      </div>
      <div>
        <h1 class="font-display text-2xl font-bold text-primary tracking-tight leading-none">TalentOS</h1>
        <p class="text-xs text-primary/70 mt-1 font-medium">{{ role === 'hr' ? '企业人力资源 AI' : '员工服务中心' }}</p>
      </div>
    </div>

    <button class="bg-primary text-on-primary w-full py-3 px-4 rounded-xl font-medium text-sm mb-8 flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-primary/20 transition-all transform hover:-translate-y-0.5">
      <span class="material-symbols-outlined text-[18px]">add</span>
      {{ role === 'hr' ? '发布新职位' : '新建申请' }}
    </button>

    <ul class="flex-1 space-y-1.5">
      <li v-for="item in items" :key="item.id">
        <button
          @click="$emit('navigate', item.id)"
          :class="['w-full flex items-center gap-3 py-2.5 px-3 rounded-xl transition-all duration-200 text-sm font-medium', currentView === item.id ? 'text-primary font-bold bg-primary/10 border border-primary/20 shadow-sm shadow-primary/5' : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low']"
        >
          <span 
            class="material-symbols-outlined" 
            :style="{ fontVariationSettings: currentView === item.id ? '\'FILL\' 1' : '\'FILL\' 0' }"
          >
            {{ item.icon }}
          </span>
          {{ item.label }}
        </button>
      </li>
    </ul>

    <div class="mt-auto border-t border-outline-variant/30 pt-4">
      <ul class="space-y-1.5 mb-4">
        <li>
          <button class="w-full flex items-center gap-3 py-2.5 px-3 rounded-xl text-on-surface-variant hover:text-primary hover:bg-primary-container/5 transition-all duration-200 text-sm font-medium">
            <span class="material-symbols-outlined">settings</span>
            系统设置
          </button>
        </li>
        <li>
          <button class="w-full flex items-center gap-3 py-2.5 px-3 rounded-xl text-on-surface-variant hover:text-primary hover:bg-primary-container/5 transition-all duration-200 text-sm font-medium">
            <span class="material-symbols-outlined">help</span>
            帮助中心
          </button>
        </li>
      </ul>
      
      <div class="flex items-center gap-3 px-3 py-3 bg-surface-container-low rounded-xl cursor-pointer hover:bg-surface-container transition-colors">
        <img 
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuCrxqatEHDCXw88vrI_yjVcbb-S0UQKZYDPRmMJ2L8wJtEy0DYS0i0W4nE1L0U_Ks54MgkryE9ck-_dfxqWl3lHFBEY5lCh1xmnR1TuPSnQvchrafaVeAP8WibX2NHz92gFp_qqqTLrrVRtn_T0BSqFVOrSXUoOgk4-Be9JXUpzeU7aqHTP8-LZ7eeY_yQYWohSQOKQbzxch1Q-aF_ZrcDOImPm6QzaN1mjOAari_cfazlK_Bwy4H01sjsVz9SvVoTqomLOvf5bJdVO" 
          alt="User Avatar" 
          class="w-10 h-10 rounded-full object-cover border border-outline-variant/50"
        />
        <div class="flex-1 min-w-0">
          <p class="font-label-md text-sm font-medium text-on-surface truncate">张伟</p>
          <p class="font-body-md text-xs text-on-surface-variant truncate">{{ role === 'hr' ? 'HR 总监' : '高级工程师' }}</p>
        </div>
        <span class="material-symbols-outlined text-on-surface-variant text-[18px]">more_vert</span>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import type { ViewType, NavItem, Role } from '../types';

defineProps<{
  role: Role;
  currentView: ViewType;
  items: NavItem[];
}>();

defineEmits<{
  (e: 'navigate', view: ViewType): void;
}>();
</script>
