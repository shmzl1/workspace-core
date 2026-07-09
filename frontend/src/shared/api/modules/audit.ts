import apiClient from '../apiClient';

export interface AuditLog {
  id: number;
  actor_user_id: number | null;
  actor_role: string;
  target_employee_id: number | null;
  action: string;
  resource_type: string;
  result: string;
  reason: string | null;
  trace_id: string | null;
  created_at: string;
  ip_address?: string | null;
  user_agent?: string | null;
}

export async function fetchAuditLogs(limit = 100): Promise<AuditLog[]> {
  const response = await apiClient.get<AuditLog[]>('/audit/logs', { params: { limit } });
  return response.data;
}
