/**
 * 考勤模块 API
 */
import apiClient from '../apiClient';
import type { AttendanceRecord } from '../types';

export interface WeeklyAttendanceSummary {
  attendance_date: string;
  status: AttendanceRecord['status'];
  check_in_at: string | null;
  check_out_at: string | null;
}

export async function fetchTodayAttendance(): Promise<AttendanceRecord | null> {
  const response = await apiClient.get<AttendanceRecord | null>('/attendance/today');
  return response.data;
}

export async function checkIn(): Promise<{ message: string; record: AttendanceRecord }> {
  const response = await apiClient.post('/attendance/check-in');
  return response.data;
}

export async function checkOut(): Promise<{ message: string; record: AttendanceRecord }> {
  const response = await apiClient.post('/attendance/check-out');
  return response.data;
}

export async function fetchWeeklyAttendance(): Promise<WeeklyAttendanceSummary[]> {
  const response = await apiClient.get<WeeklyAttendanceSummary[]>('/attendance/weekly');
  return response.data;
}

export async function fetchMonthlyAttendanceSummary(year: number, month: number, employeeId?: number): Promise<any> {
  const params: any = { year, month };
  if (employeeId) params.employee_id = employeeId;
  const response = await apiClient.get('/attendance/monthly', { params });
  return response.data;
}

