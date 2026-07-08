import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import type { Role } from '../../types';

// Welcome
import WelcomeView from '../../views/WelcomeView.vue';

// HR views
import DashboardView from '../../views/DashboardView.vue';
import CandidateDetailView from '../../views/CandidateDetailView.vue';
import InterviewsView from '../../views/InterviewsView.vue';
import ReportingView from '../../views/ReportingView.vue';
import PolicyView from '../../views/PolicyView.vue';
import AuditView from '../../views/AuditView.vue';
import SettingsView from '../../views/SettingsView.vue';

// Employee views
import EmpDashboardView from '../../views/EmpDashboardView.vue';
import AttendanceView from '../../views/AttendanceView.vue';
import LeaveView from '../../views/LeaveView.vue';
import PayrollView from '../../views/PayrollView.vue';
import EmpPolicyView from '../../views/EmpPolicyView.vue';
import EmpAssistantView from '../../views/EmpAssistantView.vue';

// 扩展 vue-router 的 RouteMeta
declare module 'vue-router' {
  interface RouteMeta {
    role: Role | null;
    label: string;
  }
}

export type RouteMeta = import('vue-router').RouteMeta;

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'welcome',
    component: WelcomeView,
    meta: { role: null, label: '欢迎' },
  },
  // ── HR routes ──
  {
    path: '/hr/dashboard',
    name: 'hr-dashboard',
    component: DashboardView,
    meta: { role: 'hr', label: '智能招聘看板' },
  },
  {
    path: '/hr/candidates',
    name: 'hr-candidates',
    component: CandidateDetailView,
    meta: { role: 'hr', label: '候选人池' },
  },
  {
    path: '/hr/interviews',
    name: 'hr-interviews',
    component: InterviewsView,
    meta: { role: 'hr', label: '面试日历' },
  },
  {
    path: '/hr/reporting',
    name: 'hr-reporting',
    component: ReportingView,
    meta: { role: 'hr', label: '招聘报告' },
  },
  {
    path: '/hr/policy',
    name: 'hr-policy',
    component: PolicyView,
    meta: { role: 'hr', label: '制度问答' },
  },
  {
    path: '/hr/audit',
    name: 'hr-audit',
    component: AuditView,
    meta: { role: 'hr', label: '权限审计' },
  },
  {
    path: '/hr/settings',
    name: 'hr-settings',
    component: SettingsView,
    meta: { role: 'hr', label: '系统设置' },
  },
  // ── Employee routes ──
  {
    path: '/employee/dashboard',
    name: 'emp-dashboard',
    component: EmpDashboardView,
    meta: { role: 'employee', label: '首页' },
  },
  {
    path: '/employee/attendance',
    name: 'emp-attendance',
    component: AttendanceView,
    meta: { role: 'employee', label: '考勤签到' },
  },
  {
    path: '/employee/leave',
    name: 'emp-leave',
    component: LeaveView,
    meta: { role: 'employee', label: '假期查询' },
  },
  {
    path: '/employee/payroll',
    name: 'emp-payroll',
    component: PayrollView,
    meta: { role: 'employee', label: '薪资明细' },
  },
  {
    path: '/employee/policy',
    name: 'emp-policy',
    component: EmpPolicyView,
    meta: { role: 'employee', label: '政策中心' },
  },
  {
    path: '/employee/assistant',
    name: 'emp-assistant',
    component: EmpAssistantView,
    meta: { role: 'employee', label: '智能助手' },
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
