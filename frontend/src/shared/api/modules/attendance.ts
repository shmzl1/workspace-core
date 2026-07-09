/**
 * 考勤模块 API
 */
import apiClient from '../apiClient';
import type { AttendanceRecord } from '../types';

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

export async function fetchWeeklyAttendance(): Promise<AttendanceRecord[]> {
  const response = await apiClient.get<AttendanceRecord[]>('/attendance/weekly');
  return response.data;
}
