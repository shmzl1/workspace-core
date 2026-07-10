export interface AuthUser {
  id: number;
  username: string;
  role: 'EMPLOYEE' | 'DEPARTMENT_MANAGER' | 'HR_SPECIALIST' | 'PAYROLL_ADMIN';
  permissions: string[];
  employee_id: number | null;
  full_name: string | null;
  department: string | null;
  job_title: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
  user: AuthUser;
}
