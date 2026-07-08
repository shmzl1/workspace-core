export type Role = 'hr' | 'employee';

export type ViewType = 
  | 'welcome'
  | 'dashboard'
  | 'pipeline'
  | 'interviews'
  | 'employees'
  | 'reporting'
  | 'assistant'
  | 'policy'
  | 'emp_dashboard'
  | 'attendance'
  | 'leave'
  | 'payroll'
  | 'emp_policy'
  | 'emp_assistant'
  | 'candidate_detail';

export interface NavItem {
  id: ViewType;
  label: string;
  icon: string;
}

export const MAIN_NAV: NavItem[] = [
  { id: 'dashboard', label: '仪表盘', icon: 'dashboard' },
  { id: 'pipeline', label: '人才库', icon: 'group_add' },
  { id: 'interviews', label: '面试安排', icon: 'calendar_today' },
  { id: 'employees', label: '员工管理', icon: 'badge' },
  { id: 'reporting', label: '数据报表', icon: 'analytics' },
  { id: 'assistant', label: '智能助手', icon: 'smart_toy' }
];

export const EMP_NAV: NavItem[] = [
  { id: 'emp_dashboard', label: '首页', icon: 'home' },
  { id: 'attendance', label: '考勤签到', icon: 'how_to_reg' },
  { id: 'leave', label: '假期查询', icon: 'event_available' },
  { id: 'payroll', label: '薪资明细', icon: 'account_balance_wallet' },
  { id: 'emp_policy', label: '政策中心', icon: 'policy' },
  { id: 'emp_assistant', label: '智能助手', icon: 'smart_toy' }
];
