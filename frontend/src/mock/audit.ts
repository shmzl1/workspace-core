/**
 * 审计 Mock 数据
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
    operator_role: 'HR专员',
    resource: '/api/v1/salary/access_control',
    action: 'READ',
    result: 'ALLOWED',
    timestamp: '2026-07-08T09:30:00Z',
    ip_address: '192.168.1.102',
    trace_id: 'trace-aa11bb22',
    target_employee: '张伟',
    detail: 'HR 查看员工薪资访问权限',
  },
  {
    id: 2,
    operator_name: '张伟',
    operator_department: '研发部',
    operator_role: '高级工程师',
    resource: '/api/v1/salary/access_control',
    action: 'READ',
    result: 'DENIED',
    timestamp: '2026-07-08T08:15:00Z',
    ip_address: '10.0.4.15',
    trace_id: 'trace-cc33dd44',
    target_employee: '李明',
    detail: '普通员工尝试查询他人薪资 - 已拦截',
  },
  {
    id: 3,
    operator_name: '李明',
    operator_department: '研发部',
    operator_role: '研发经理',
    resource: '/api/v1/employees/export',
    action: 'WRITE',
    result: 'PENDING',
    timestamp: '2026-07-08T07:00:00Z',
    ip_address: '10.0.4.12',
    trace_id: 'trace-ee55ff66',
    detail: '导出员工数据 - 待审核',
  },
  {
    id: 4,
    operator_name: '王强',
    operator_department: '运维部',
    operator_role: '系统管理员',
    resource: '/api/v1/admin/roles/update',
    action: 'WRITE',
    result: 'ALLOWED',
    timestamp: '2026-07-07T14:00:00Z',
    ip_address: '192.168.1.1',
    trace_id: 'trace-gg77hh88',
    detail: '更新角色权限配置',
  },
  {
    id: 5,
    operator_name: '赵敏',
    operator_department: '财务部',
    operator_role: '薪酬管理员',
    resource: '/api/v1/payroll/review',
    action: 'READ',
    result: 'ALLOWED',
    timestamp: '2026-07-08T10:00:00Z',
    ip_address: '192.168.1.105',
    trace_id: 'trace-ii99jj00',
    target_employee: '张伟',
    detail: '薪酬管理员查看员工薪资预审',
  },
];

export const mockAuditStats = {
  security_score: 94,
  monitored_modules: 48,
  sensitive_access_24h: 1245,
  anomaly_events: 1,
};
