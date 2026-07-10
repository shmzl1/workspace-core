/**
 * 员工 / 假期 / 薪资模块 API
 */
import apiClient from '../apiClient';
import type { Employee, LeaveBalance } from '../types';

export interface EmployeeProfile {
  employee: Employee;
  leave_balance: LeaveBalance | null;
}

// ── 员工 ───────────────────────────────────

export async function fetchMyProfile(): Promise<EmployeeProfile> {
  const response = await apiClient.get<EmployeeProfile>('/employees/me');
  return response.data;
}

// ── 假期 ───────────────────────────────────

export async function fetchLeaveBalance(year?: number): Promise<LeaveBalance> {
  const response = await apiClient.get<LeaveBalance>('/employees/me/leave-balance', { params: { year } });
  return response.data;
}

// ── 薪资 ───────────────────────────────────

export interface PayrollSummary {
  year: number;
  month: number;
  gross_salary: number;
  net_salary: number;
  deductions: Record<string, number>;
}

export async function fetchPayrollSummary(year?: number, month?: number): Promise<PayrollSummary[]> {
  const response = await apiClient.get<PayrollSummary[]>('/payroll/me', { params: { year, month } });
  return response.data;
}

export async function fetchEmployees(): Promise<Employee[]> {
  const response = await apiClient.get<Employee[]>('/employees');
  return response.data;
}
