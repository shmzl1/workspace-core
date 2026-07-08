/**
 * 审计样例数据
 */
export interface AuditLogEntry {
  id: number;
  operator_name: string;
  operator_department: string;
  operator_role: string;
  resource: string;
  action: string;
  result: 'ALLOWED' | 'DENIED' | 'PENDING';
  timestamp: string;
  ip_address: string;
  trace_id: string;
  target_employee?: string;
  detail?: string;
}

export const mockAuditLogs: AuditLogEntry[] = [
  {
    id: 1,
    operator_name: '林雨晴',
    operator_department: '招聘部',
    operator_role: 'HR 专员',
    resource: '/api/v1/payroll/access-control',
    action: 'READ',
    result: 'ALLOWED',
    timestamp: '2026-07-08T09:30:00Z',
    ip_address: '192.168.1.102',
    trace_id: 'trace-aa11bb22',
    target_employee: '张伟',
    detail: '查看员工薪资访问权限',
  },
  {
    id: 2,
    operator_name: '张伟',
    operator_department: '研发部',
    operator_role: '高级工程师',
    resource: '/api/v1/payroll/access-control',
    action: 'READ',
    result: 'DENIED',
    timestamp: '2026-07-08T08:15:00Z',
    ip_address: '10.0.4.15',
    trace_id: 'trace-cc33dd44',
    target_employee: '李明',
    detail: '越权查看他人薪资被拒绝',
  },
];

export const mockAuditStats = {
  security_score: 94,
  monitored_modules: 48,
  sensitive_access_24h: 1245,
  anomaly_events: 1,
};
