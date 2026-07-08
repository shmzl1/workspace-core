<template>
  <template v-if="route.name === 'welcome'">
    <router-view
      @navigate="handleNavigate"
      @show-toast="showToast"
    />
    <ToastMessage :message="toastMessage" />
  </template>
  <template v-else>
    <div class="app-shell">
      <AppTopbar />
      <AppSidebar
        :active-route="route.path"
        :role="role"
        @navigate="handleNavigate"
        @toggleRole="handleToggleRole"
      />
      <main class="app-shell__main">
        <router-view
          :page-title="currentLabel"
          :trace-logs="traceLogs"
          :role="role"
          @export-report="handleExportReport"
          @navigate="handleNavigate"
          @show-toast="showToast"
        />
      </main>
      <GlobalAgentBar :role="role" @submit-command="handleAgentCommand" />
      <ToastMessage :message="toastMessage" />
    </div>
  </template>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import type { Role } from '../types';
import { getSavedRole, setSavedRole, getDefaultRoute } from '../app/router/guards';
import AppTopbar from './AppTopbar.vue';
import AppSidebar from './AppSidebar.vue';
import GlobalAgentBar from './GlobalAgentBar.vue';
import ToastMessage from '../shared/components/base/ToastMessage.vue';
import { initialTraceLogs } from '../mock/recruitmentDashboard';

const router = useRouter();
const route = useRoute();

const role = ref<Role>(getSavedRole());
const toastMessage = ref('');
const traceLogs = ref<string[]>([...initialTraceLogs]);
let toastTimer: number | undefined;

const currentLabel = computed(() => {
  return (route.meta?.label as string) ?? '';
});

function showToast(message: string) {
  toastMessage.value = message;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    toastMessage.value = '';
  }, 2400);
}

function handleNavigate(view: string) {
  const routeMap: Record<string, string> = {
    'dashboard': '/hr/dashboard',
    'pipeline': '/hr/candidates',
    'candidate_detail': '/hr/candidates',
    'interviews': '/hr/interviews',
    'candidates': '/hr/candidates',
    'reporting': '/hr/reporting',
    'assistant': '/hr/assistant',
    'policy': '/hr/policy',
    'audit': '/hr/audit',
    'settings': '/hr/settings',
    'emp_dashboard': '/employee/dashboard',
    'attendance': '/employee/attendance',
    'leave': '/employee/leave',
    'payroll': '/employee/payroll',
    'emp_policy': '/employee/policy',
    'emp_assistant': '/employee/assistant',
  };

  if (view === 'welcome') {
    router.push('/');
    return;
  }

  const path = routeMap[view];
  if (path) {
    router.push(path);
  }
}

function handleToggleRole() {
  const newRole: Role = role.value === 'hr' ? 'employee' : 'hr';
  role.value = newRole;
  setSavedRole(newRole);
  router.push(getDefaultRoute(newRole));
}

function handleExportReport() {
  showToast('招聘报告预览已生成。');
}

function handleAgentCommand(command: string) {
  if (!command.trim()) return;

  traceLogs.value = [`已接收任务：${command}`, ...traceLogs.value].slice(0, 5);
  showToast('智能助手任务已提交。');

  window.setTimeout(() => {
    traceLogs.value = ['任务规划完成，正在汇总业务建议。', ...traceLogs.value].slice(0, 5);
  }, 2000);
}
</script>

<style scoped lang="scss">
.app-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 12%, rgba(36, 85, 245, 0.08), transparent 32%),
    var(--color-bg);
}

.app-shell__main {
  min-height: calc(100vh - var(--topbar-height));
  margin-left: var(--sidebar-width);
  padding: 28px 34px calc(var(--agentbar-height) + 30px);
}

@media (max-width: 980px) {
  .app-shell__main {
    margin-left: 0;
    padding: 24px 18px calc(var(--agentbar-height) + 36px);
  }
}
</style>
