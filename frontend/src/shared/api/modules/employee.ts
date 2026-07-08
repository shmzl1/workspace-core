/**
 * 员工 / 假期 / 薪资模块 API
 */
import apiClient from '../apiClient';
import type { ApiResponse, Employee, LeaveBalance } from '../types';

// ── 员工 ───────────────────────────────────

export async function fetchMyProfile(): Promise<ApiResponse<Employee>> {
  return apiClient.get('/employees/me');
}

// ── 假期 ───────────────────────────────────

export async function fetchLeaveBalance(year?: number): Promise<ApiResponse<LeaveBalance>> {
  return apiClient.get('/leave/balance', { params: { year } });
}

// ── 薪资 ───────────────────────────────────

export interface PayrollSummary {
  year: number;
  month: number;
  gross_salary: number;
  net_salary: number;
  deductions: Record<string, number>;
}

export async function fetchPayrollSummary(year?: number, month?: number): Promise<ApiResponse<PayrollSummary[]>> {
  return apiClient.get('/payroll/me', { params: { year, month } });
}
