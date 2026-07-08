<template>
  <template v-if="activeItem === 'welcome'">
    <component 
      :is="currentViewComponent"
      @navigate="handleNavigate"
      @show-toast="showToast"
    />
    <ToastMessage :message="toastMessage" />
  </template>
  <template v-else>
    <div class="app-shell">
      <AppTopbar />
      <AppSidebar 
        :active-item="activeItem" 
        :role="role"
        @select="handleSidebarSelect" 
        @toggleRole="handleToggleRole"
      />
      <main class="app-shell__main">
        <component 
          :is="currentViewComponent"
          :page-title="activeItem"
          :trace-logs="traceLogs"
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
import type { Role } from '../types';
import AppTopbar from './AppTopbar.vue';
import AppSidebar from './AppSidebar.vue';
import GlobalAgentBar from './GlobalAgentBar.vue';
import ToastMessage from '../shared/components/base/ToastMessage.vue';
import { initialTraceLogs } from '../shared/data/recruitmentDashboard';

// Import initial views
import DashboardView from '../views/DashboardView.vue';
import CandidateDetailView from '../views/CandidateDetailView.vue';
import InterviewsView from '../views/InterviewsView.vue';
import ReportingView from '../views/ReportingView.vue';
import PolicyView from '../views/PolicyView.vue';
import WelcomeView from '../views/WelcomeView.vue';
import EmpDashboardView from '../views/EmpDashboardView.vue';
import AttendanceView from '../views/AttendanceView.vue';
import LeaveView from '../views/LeaveView.vue';
import PayrollView from '../views/PayrollView.vue';
import EmpPolicyView from '../views/EmpPolicyView.vue';
import EmpAssistantView from '../views/EmpAssistantView.vue';
import AuditView from '../views/AuditView.vue';
import SettingsView from '../views/SettingsView.vue';

const role = ref<Role>('hr');
const activeItem = ref('welcome');
const toastMessage = ref('');
const traceLogs = ref<string[]>([...initialTraceLogs]);
let toastTimer: number | undefined;

const currentViewComponent = computed(() => {
  switch (activeItem.value) {
    case 'welcome': return WelcomeView;
    case '智能招聘看板': return DashboardView;
    case '候选人池': return CandidateDetailView;
    case '面试日历':
    case '面试安排': return InterviewsView;
    case '招聘报告': return ReportingView;
    case '制度问答': return PolicyView;
    case '权限审计': return AuditView;
    case '系统设置': return SettingsView;
    case '首页': return EmpDashboardView;
    case '考勤签到': return AttendanceView;
    case '假期查询': return LeaveView;
    case '薪资明细': return PayrollView;
    case '政策中心': return EmpPolicyView;
    case '智能助手': return EmpAssistantView;
    default: return DashboardView;
  }
});

function showToast(message: string) {
  toastMessage.value = message;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    toastMessage.value = '';
  }, 2400);
}

function handleSidebarSelect(item: string) {
  activeItem.value = item;
}

function handleToggleRole() {
  if (role.value === 'hr') {
    role.value = 'employee';
    activeItem.value = '首页';
  } else {
    role.value = 'hr';
    activeItem.value = '智能招聘看板';
  }
}

function handleNavigate(view: string) {
  const hrViews = ['dashboard', 'pipeline', 'candidate_detail', 'interviews', 'reporting', 'policy', 'audit', 'settings'];
  const employeeViews = ['emp_dashboard', 'attendance', 'leave', 'payroll', 'emp_policy', 'emp_assistant'];
  
  if (hrViews.includes(view)) {
    role.value = 'hr';
  } else if (employeeViews.includes(view)) {
    role.value = 'employee';
  }

  const viewMap: Record<string, string> = {
    'dashboard': '智能招聘看板',
    'pipeline': '候选人池',
    'candidate_detail': '候选人池',
    'interviews': '面试日历',
    'reporting': '招聘报告',
    'policy': '制度问答',
    'audit': '权限审计',
    'settings': '系统设置',
    'emp_dashboard': '首页',
    'attendance': '考勤签到',
    'leave': '假期查询',
    'payroll': '薪资明细',
    'emp_policy': '政策中心',
    'emp_assistant': '智能助手'
  };
  if (viewMap[view]) {
    activeItem.value = viewMap[view];
  } else {
    activeItem.value = view;
  }
}

function handleExportReport() {
  showToast('招聘报告预览已生成。');
}

function handleAgentCommand(command: string) {
  if (!command.trim()) {
    return;
  }

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
