<template>
  <router-view v-if="route.name === 'login' || route.name === 'welcome'" />
  <div v-else-if="currentUser" class="app-shell">
    <AppTopbar :user="currentUser" @logout="handleLogout" />
    <AppSidebar :active-route="route.path" :user="currentUser" @navigate="handleNavigate" />
    <main class="app-shell__main">
      <router-view :page-title="currentLabel" :trace-logs="traceLogs" :role="agentRole" @navigate="handleNavigate" @show-toast="showToast" />
    </main>
    <ToastMessage :message="toastMessage" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getDefaultRoute, useAuthStore } from '../features/auth/authStore';
import AppTopbar from './AppTopbar.vue';
import AppSidebar from './AppSidebar.vue';
import ToastMessage from '../shared/components/base/ToastMessage.vue';

const router = useRouter();
const route = useRoute();
const { currentUser, logout } = useAuthStore();
const toastMessage = ref('');
// Only server-provided, auditable Agent events may be displayed here.
const traceLogs = ref<string[]>([]);
let toastTimer: number | undefined;
const currentLabel = computed(() => String(route.meta.label || ''));
const agentRole = computed(() => currentUser.value?.permissions.includes('agent.hr.use') ? 'hr' : 'employee');

function showToast(message: string) {
  toastMessage.value = message;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => { toastMessage.value = ''; }, 2400);
}

function handleNavigate(view: string) {
  let targetView = view;
  if (view === 'emp_assistant' && agentRole.value === 'hr') {
    targetView = 'assistant';
  } else if (view === 'assistant' && agentRole.value === 'employee') {
    targetView = 'emp_assistant';
  }
  const routeMap: Record<string, string> = {
    dashboard: '/hr/dashboard', evaluation: '/hr/evaluation', pipeline: '/hr/pipeline', candidates: '/hr/candidates', interviews: '/hr/interviews',
    reporting: '/hr/reporting', assistant: '/hr/assistant', policy: '/hr/policy', audit: '/hr/audit', settings: '/hr/settings',
    emp_dashboard: '/employee/dashboard', attendance: '/employee/attendance', leave: '/employee/leave', payroll: '/employee/payroll',
    emp_policy: '/employee/policy', emp_assistant: '/employee/assistant', attendance_review: '/employee/attendance-review',
  };
  router.push(routeMap[targetView] || getDefaultRoute());
}

function handleLogout() {
  logout();
  router.replace('/login');
}
</script>

<style scoped lang="scss">
.app-shell { min-height: 100vh; background: var(--color-bg); }
.app-shell__main { min-height: calc(100vh - var(--topbar-height)); margin-left: var(--sidebar-width); padding: 28px 34px 30px; }
@media (max-width: 980px) { .app-shell__main { margin-left: 0; padding: 24px 18px 36px; } }
</style>
