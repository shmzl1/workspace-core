import apiClient from '../apiClient';

export interface SalaryDetail {
  id: number;
  employee_id: number;
  base_salary: number | null;
  currency: string | null;
  effective_from: string | null;
  effective_to: string | null;
}

export async function fetchMySalary(): Promise<SalaryDetail> {
  const response = await apiClient.get<SalaryDetail>('/payroll/me');
  return response.data;
}

export async function fetchEmployeeSalary(employeeId: number): Promise<SalaryDetail> {
  const response = await apiClient.get<SalaryDetail>(`/payroll/employee/${employeeId}`);
  return response.data;
}
