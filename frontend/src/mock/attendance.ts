/**
 * 鑰冨嫟 样例数据
 */
import type { AttendanceRecord } from '../shared/api/types';

export const mockTodayAttendance: AttendanceRecord = {
  id: 1,
  employee_id: 2,
  attendance_date: '2026-07-08',
  check_in_at: null,
  check_out_at: null,
  status: 'NORMAL' as const,
  late_minutes: 0,
  early_leave_minutes: 0,
  leave_balance_id: null,
  source: 'WEB' as const,
  remark: null,
  created_at: '2026-07-08T08:55:00Z',
  updated_at: '2026-07-08T08:55:00Z',
};

export const mockCheckedIn: AttendanceRecord = {
  ...mockTodayAttendance,
  check_in_at: '2026-07-08T09:05:00Z',
  status: 'LATE' as const,
  late_minutes: 5,
  source: 'WEB' as const,
};

export const mockCheckedOut: AttendanceRecord = {
  ...mockTodayAttendance,
  check_in_at: '2026-07-08T08:55:00Z',
  check_out_at: '2026-07-08T18:05:00Z',
  status: 'NORMAL' as const,
  source: 'WEB' as const,
};

export const mockMonthlyAttendance: AttendanceRecord[] = [
  { id: 1, employee_id: 2, attendance_date: '2026-07-01', check_in_at: '2026-07-01T08:50:00Z', check_out_at: '2026-07-01T18:00:00Z', status: 'NORMAL', late_minutes: 0, early_leave_minutes: 0, leave_balance_id: null, source: 'WEB', remark: null, created_at: '2026-07-01T08:50:00Z', updated_at: '2026-07-01T18:00:00Z' },
  { id: 2, employee_id: 2, attendance_date: '2026-07-02', check_in_at: '2026-07-02T09:10:00Z', check_out_at: '2026-07-02T18:00:00Z', status: 'LATE', late_minutes: 10, early_leave_minutes: 0, leave_balance_id: null, source: 'WEB', remark: null, created_at: '2026-07-02T09:10:00Z', updated_at: '2026-07-02T18:00:00Z' },
  { id: 3, employee_id: 2, attendance_date: '2026-07-03', check_in_at: '2026-07-03T08:48:00Z', check_out_at: '2026-07-03T17:30:00Z', status: 'EARLY_LEAVE', late_minutes: 0, early_leave_minutes: 30, leave_balance_id: null, source: 'WEB', remark: null, created_at: '2026-07-03T08:48:00Z', updated_at: '2026-07-03T17:30:00Z' },
  { id: 4, employee_id: 2, attendance_date: '2026-07-04', check_in_at: null, check_out_at: null, status: 'ABSENT', late_minutes: 0, early_leave_minutes: 0, leave_balance_id: null, source: 'WEB', remark: null, created_at: '2026-07-04T00:00:00Z', updated_at: '2026-07-04T00:00:00Z' },
  { id: 5, employee_id: 2, attendance_date: '2026-07-05', check_in_at: '2026-07-05T08:55:00Z', check_out_at: '2026-07-05T18:05:00Z', status: 'NORMAL', late_minutes: 0, early_leave_minutes: 0, leave_balance_id: null, source: 'WEB', remark: null, created_at: '2026-07-05T08:55:00Z', updated_at: '2026-07-05T18:05:00Z' },
  { id: 6, employee_id: 2, attendance_date: '2026-07-07', check_in_at: '2026-07-07T08:52:00Z', check_out_at: '2026-07-07T18:00:00Z', status: 'NORMAL', late_minutes: 0, early_leave_minutes: 0, leave_balance_id: null, source: 'WEB', remark: null, created_at: '2026-07-07T08:52:00Z', updated_at: '2026-07-07T18:00:00Z' },
];

