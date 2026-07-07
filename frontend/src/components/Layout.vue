<template>
  <template v-if="currentView === 'welcome'">
    <slot />
  </template>
  <template v-else>
    <div class="flex h-screen bg-background overflow-hidden text-on-background font-body-lg">
      <Sidebar 
        :role="role" 
        :currentView="currentView" 
        :items="navItems"
        @navigate="$emit('navigate', $event)"
      />
      <div class="ml-[256px] flex-1 flex flex-col h-screen w-[calc(100%-256px)]">
        <Header 
          :role="role" 
          :currentView="currentView" 
          @toggleRole="$emit('toggleRole')"
          @navigate="$emit('navigate', $event)"
        />
        <main class="flex-1 overflow-y-auto p-6 md:p-8">
          <div class="max-w-7xl mx-auto w-full min-h-full flex flex-col">
            <slot />
          </div>
        </main>
      </div>
    </div>
  </template>
</template>

<script setup lang="ts">
import type { ViewType, Role, NavItem } from '../types';
import Sidebar from './Sidebar.vue';
import Header from './Header.vue';

defineProps<{
  role: Role;
  currentView: ViewType;
  navItems: NavItem[];
}>();

defineEmits<{
  (e: 'toggleRole'): void;
  (e: 'navigate', view: ViewType): void;
}>();
</script>
