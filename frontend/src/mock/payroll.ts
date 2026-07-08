/**
 * 薪资样例数据
 */
import type { Employee, LeaveBalance } from '../shared/api/types';
import type { PayrollSummary } from '../shared/api/modules/employee';

export const mockEmployee: Employee = {
  id: 2,
  user_id: 2,
  employee_no: 'EMP-2020-0042',
  full_name: '张伟',
  department: '研发中心',
  job_title: '高级工程师',
  manager_employee_id: 1,
  email: 'zhangwei@talentflow.local',
  phone: '13800001111',
  hire_date: '2020-03-01',
  employment_status: 'ACTIVE',
  created_at: '2020-03-01T00:00:00Z',
  updated_at: '2026-07-01T00:00:00Z',
};

export const mockLeaveBalance: LeaveBalance = {
  id: 1,
  employee_id: 2,
  leave_type: 'ANNUAL',
  year: 2026,
  total_days: 15,
  used_days: 3,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-07-01T00:00:00Z',
};

export const mockPayrollSummaries: PayrollSummary[] = [
  {
    year: 2026,
    month: 7,
    gross_salary: 35000,
    net_salary: 28450,
    deductions: {
      social_insurance: 2800,
      housing_fund: 1400,
      income_tax: 2350,
    },
  },
];

export const mockPayrollDetail = {
  year: 2026,
  month: 7,
  checkOutAt: '2026-07-31T18:00:00Z',
  gross_salary: 35000,
  net_salary: 28450,
  breakdown: {
    base_salary: 25000,
    performance_bonus: 8000,
    allowances: 2000,
  },
  deductions: {
    social_insurance: 2800,
    housing_fund: 1400,
    income_tax: 2350,
  },
  deduction_details: [
    { name: '社保公积金个人部分', amount: 4200, note: '基数：25000' },
    { name: '个人所得税', amount: 2350, note: '已扣除专项附加' },
  ],
};
