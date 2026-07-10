import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import LoginView from '../../features/auth/LoginView.vue';

// HR views
import RecruitmentDashboardPage from '../../features/recruitment/dashboard/RecruitmentDashboardPage.vue';
import DashboardView from '../../views/DashboardView.vue';
import CandidateDetailView from '../../views/CandidateDetailView.vue';
import InterviewsView from '../../views/InterviewsView.vue';
import ReportingView from '../../views/ReportingView.vue';
import AssistantView from '../../views/AssistantView.vue';
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
    label: string;
    requiresAuth?: boolean;
    anyPermissions?: string[];
  }
}

export type RouteMeta = import('vue-router').RouteMeta;

const routes: RouteRecordRaw[] = [
  {
    path: '/', redirect: '/login',
  },
  {
    path: '/login', name: 'login', component: LoginView, meta: { label: '登录' },
  },
  // ── HR routes ──
  {
    path: '/hr/dashboard',
    name: 'hr-dashboard',
    component: RecruitmentDashboardPage,
    meta: { requiresAuth: true, anyPermissions: ['recruitment.read'], label: '智能招聘看板' },
  },
  {
    path: '/hr/pipeline',
    name: 'hr-pipeline',
    component: DashboardView,
    meta: { requiresAuth: true, anyPermissions: ['candidate.read'], label: '智能筛选' },
  },
  {
    path: '/hr/candidates',
    name: 'hr-candidates',
    component: CandidateDetailView,
    meta: { requiresAuth: true, anyPermissions: ['candidate.read'], label: '候选人池' },
  },
  {
    path: '/hr/interviews',
    name: 'hr-interviews',
    component: InterviewsView,
    meta: { requiresAuth: true, anyPermissions: ['interview.read'], label: '面试日历' },
  },
  {
    path: '/hr/reporting',
    name: 'hr-reporting',
    component: ReportingView,
    meta: { requiresAuth: true, anyPermissions: ['reporting.recruitment.read'], label: '招聘报告' },
  },
  {
    path: '/hr/assistant',
    name: 'hr-assistant',
    component: AssistantView,
    meta: { requiresAuth: true, anyPermissions: ['agent.hr.use'], label: '智能助手' },
  },
  {
    path: '/hr/policy',
    name: 'hr-policy',
    component: PolicyView,
    meta: { requiresAuth: true, anyPermissions: ['policy.read'], label: '制度问答' },
  },
  {
    path: '/hr/audit',
    name: 'hr-audit',
    component: AuditView,
    meta: { requiresAuth: true, anyPermissions: ['audit.read'], label: '权限审计' },
  },
  {
    path: '/hr/settings',
    name: 'hr-settings',
    component: SettingsView,
    meta: { requiresAuth: true, anyPermissions: ['recruitment.manage'], label: '系统设置' },
  },
  // ── Employee routes ──
  {
    path: '/employee/dashboard',
    name: 'emp-dashboard',
    component: EmpDashboardView,
    meta: { requiresAuth: true, anyPermissions: ['attendance.self.read'], label: '首页' },
  },
  {
    path: '/employee/attendance',
    name: 'emp-attendance',
    component: AttendanceView,
    meta: { requiresAuth: true, anyPermissions: ['attendance.self.read'], label: '考勤签到' },
  },
  {
    path: '/employee/leave',
    name: 'emp-leave',
    component: LeaveView,
    meta: { requiresAuth: true, anyPermissions: ['leave.self.read'], label: '假期查询' },
  },
  {
    path: '/employee/payroll',
    name: 'emp-payroll',
    component: PayrollView,
    meta: { requiresAuth: true, anyPermissions: ['payroll.self.read', 'payroll.department.read', 'payroll.masked.read', 'payroll.all.read'], label: '薪资明细' },
  },
  {
    path: '/employee/policy',
    name: 'emp-policy',
    component: EmpPolicyView,
    meta: { requiresAuth: true, anyPermissions: ['policy.read'], label: '政策中心' },
  },
  {
    path: '/employee/assistant',
    name: 'emp-assistant',
    component: EmpAssistantView,
    meta: { requiresAuth: true, anyPermissions: ['agent.employee.use'], label: '智能助手' },
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
