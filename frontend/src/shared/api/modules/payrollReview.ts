import apiClient from '../apiClient';
import type { PayrollPreAuditRequest, PayrollPreAuditResponse } from '../types';

export async function reviewPayrollPreAudit(
  payload: PayrollPreAuditRequest
): Promise<PayrollPreAuditResponse> {
  const response = await apiClient.post<PayrollPreAuditResponse>('/payroll-review/pre-audit', payload);
  return response.data;
}

export const fetchPayrollPreAudit = reviewPayrollPreAudit;
