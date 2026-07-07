<template>
  <div class="app-shell">
    <AppTopbar />
    <AppSidebar :active-item="activeItem" @select="handleSidebarSelect" />
    <main class="app-shell__main">
      <RecruitmentDashboardPage
        :page-title="activeItem"
        :trace-logs="traceLogs"
        @export-report="handleExportReport"
      />
    </main>
    <GlobalAgentBar @submit-command="handleAgentCommand" />
    <ToastMessage :message="toastMessage" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppTopbar from './AppTopbar.vue';
import AppSidebar from './AppSidebar.vue';
import GlobalAgentBar from './GlobalAgentBar.vue';
import ToastMessage from '../components/base/ToastMessage.vue';
import RecruitmentDashboardPage from '../features/recruitment-dashboard/RecruitmentDashboardPage.vue';
import { initialTraceLogs } from '../mock/recruitmentDashboard';

const activeItem = ref('智能招聘看板');
const toastMessage = ref('');
const traceLogs = ref<string[]>([...initialTraceLogs]);
let toastTimer: number | undefined;

function showToast(message: string) {
  toastMessage.value = message;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    toastMessage.value = '';
  }, 2400);
}

function handleSidebarSelect(item: string) {
  activeItem.value = item;
  showToast('当前为前端演示模式，模块内容将在后续 Sprint 接入。');
}

function handleExportReport() {
  showToast('招聘报告已生成演示预览。');
}

function handleAgentCommand(command: string) {
  if (!command.trim()) {
    return;
  }

  traceLogs.value = [`已接收任务：${command}`, ...traceLogs.value].slice(0, 5);
  showToast('Agent 演示任务已提交。');

  window.setTimeout(() => {
    traceLogs.value = ['任务规划完成，等待后端 Agent 接入。', ...traceLogs.value].slice(0, 5);
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
