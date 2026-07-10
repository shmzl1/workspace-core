import apiClient from '../apiClient';
import type { PayrollPreAuditRequest, PayrollPreAuditResponse } from '../types';

export interface PayrollReviewSummary {
  id: number;
  employee_id: number;
  employee_name: string | null;
  period_code: string | null;
  status: string;
  net_salary_preview: number;
}

export async function fetchPayrollReviewRecords(): Promise<{ records: PayrollReviewSummary[] }> {
  const response = await apiClient.get<{ records: PayrollReviewSummary[] }>('/payroll-review/records');
  return response.data;
}

export async function reviewPayrollPreAudit(
  payload: PayrollPreAuditRequest
): Promise<PayrollPreAuditResponse> {
  const response = await apiClient.post<PayrollPreAuditResponse>('/payroll-review/pre-audit', payload);
  return response.data;
}

export const fetchPayrollPreAudit = reviewPayrollPreAudit;
