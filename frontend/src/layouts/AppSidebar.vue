<template>
  <aside class="sidebar">
    <div class="sidebar__groups"><section v-for="group in currentGroups" :key="group.title" class="sidebar__group"><h2>{{ group.title }}</h2><button v-for="item in group.items" :key="item.path" class="sidebar__item" :class="{ 'sidebar__item--active': isActive(item) }" @click="$emit('navigate', item.id)"><span class="sidebar__item-mark"></span>{{ item.label }}</button></section></div>
    <div class="sidebar__profile"><span class="sidebar__avatar">{{ user.full_name?.slice(0, 1) || user.username.slice(0, 1) }}</span><div><strong>{{ user.full_name || user.username }}</strong><small>{{ user.job_title || roleLabel }}</small></div></div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AuthUser } from '../features/auth/authTypes';
interface SidebarItem { id: string; label: string; path: string; permissions: string[]; }
const props = defineProps<{ activeRoute: string; user: AuthUser }>();
defineEmits<{ navigate: [id: string] }>();
const hasAny = (permissions: string[]) => permissions.some((item) => props.user.permissions.includes(item));
const isActive = (item: SidebarItem) => {
  if (item.id === 'emp_assistant') {
    return props.activeRoute === '/employee/assistant' || props.activeRoute === '/hr/assistant';
  }
  return item.path === props.activeRoute;
};
const groups: { title: string; items: SidebarItem[] }[] = [
  { title: '工作台', items: [
    { id: 'dashboard', label: '智能招聘看板', path: '/hr/dashboard', permissions: ['recruitment.read'] },
    { id: 'evaluation', label: '多 Agent 评估', path: '/hr/evaluation', permissions: ['agent.hr.use'] },
    { id: 'candidates', label: '候选人池', path: '/hr/candidates', permissions: ['candidate.read'] },
    { id: 'interviews', label: '面试日历', path: '/hr/interviews', permissions: ['interview.read'] },
    { id: 'reporting', label: '招聘报告', path: '/hr/reporting', permissions: ['reporting.recruitment.read'] },
  ] },
  { title: '员工服务', items: [
    { id: 'emp_dashboard', label: '首页', path: '/employee/dashboard', permissions: ['attendance.self.read'] },
    { id: 'attendance', label: '考勤签到', path: '/employee/attendance', permissions: ['attendance.self.read'] },
    { id: 'leave', label: '假期查询', path: '/employee/leave', permissions: ['leave.self.read'] },
    { id: 'payroll', label: '薪资明细', path: '/employee/payroll', permissions: ['payroll.self.read', 'payroll.department.read', 'payroll.masked.read', 'payroll.all.read'] },
    { id: 'emp_policy', label: '政策中心', path: '/employee/policy', permissions: ['policy.read'] },
    { id: 'emp_assistant', label: '智能助手', path: '/employee/assistant', permissions: ['agent.employee.use', 'agent.hr.use'] },
  ] },
  { title: '管理', items: [
    { id: 'audit', label: '权限审计', path: '/hr/audit', permissions: ['audit.read'] },
    { id: 'settings', label: '系统设置', path: '/hr/settings', permissions: ['recruitment.manage'] },
  ] },
];
const currentGroups = computed(() => groups.map((group) => ({ ...group, items: group.items.filter((item) => hasAny(item.permissions)) })).filter((group) => group.items.length));
const roleLabel = computed(() => ({ EMPLOYEE: '普通员工', DEPARTMENT_MANAGER: '部门主管', HR_SPECIALIST: 'HR 专员', PAYROLL_ADMIN: '薪酬管理员' }[props.user.role] || props.user.role));
</script>

<style scoped lang="scss">
.sidebar { position: fixed; top: var(--topbar-height); bottom: 0; left: 0; z-index: 15; display: flex; width: var(--sidebar-width); flex-direction: column; justify-content: space-between; padding: 22px 16px; border-right: 1px solid var(--color-line); background: rgba(255,255,255,.86); backdrop-filter: blur(14px); }.sidebar__groups { display: grid; gap: 22px; }.sidebar__group h2 { margin: 0 0 9px 10px; color: var(--color-subtle); font-size: 12px; font-weight: 800; }.sidebar__item { display:flex; width:100%; align-items:center; gap:10px; padding:11px 12px; border-radius:var(--radius-sm); background:transparent; color:var(--color-muted); text-align:left; }.sidebar__item-mark { width:8px; height:8px; border:2px solid currentColor; border-radius:50%; }.sidebar__item--active { background:var(--color-primary-soft); color:var(--color-primary); font-weight:800; }.sidebar__profile { display:flex; align-items:center; gap:10px; padding:12px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:#fff; }.sidebar__avatar { display:grid; width:40px; height:40px; place-items:center; border-radius:50%; background:#eaf0ff; color:var(--color-primary); font-weight:800; }.sidebar__profile strong,.sidebar__profile small { display:block; }.sidebar__profile small { margin-top:3px; color:var(--color-muted); font-size:12px; } @media (max-width:980px) { .sidebar { position:static; width:auto; padding:12px 18px; }.sidebar__groups { grid-template-columns:repeat(3,minmax(0,1fr)); }.sidebar__profile { display:none; } }
</style>
