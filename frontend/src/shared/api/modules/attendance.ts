/**
 * 考勤模块 API
 *
 * 当前返回 mock 数据；后续只需将 mock 替换为 apiClient 调用即可接入后端。
 */
import apiClient from '../apiClient';
import type { ApiResponse, AttendanceRecord } from '../types';

export async function fetchTodayAttendance(): Promise<ApiResponse<AttendanceRecord | null>> {
  return apiClient.get('/attendance/today');
}

export async function checkIn(): Promise<ApiResponse<AttendanceRecord>> {
  return apiClient.post('/attendance/check-in');
}

export async function checkOut(): Promise<ApiResponse<AttendanceRecord>> {
  return apiClient.post('/attendance/check-out');
}

export async function fetchMonthlyAttendance(year: number, month: number): Promise<ApiResponse<AttendanceRecord[]>> {
  return apiClient.get('/attendance/monthly', { params: { year, month } });
}
