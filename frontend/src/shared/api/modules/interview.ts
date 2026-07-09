import apiClient from '../apiClient';
import type { SchedulePreviewRequest, SchedulePreviewResponse } from '../types';

export interface InterviewerResource {
  id: number;
  employee_id: number;
  employee_name?: string | null;
  specialties: string[];
}

export interface MeetingRoomResource {
  id: number;
  name: string;
}

export interface InterviewResource {
  id: number;
  application_id: number;
  interviewer_id: number;
  meeting_room_id: number;
  start_at: string;
  end_at: string;
  status: string;
}

export async function fetchInterviewers(): Promise<InterviewerResource[]> {
  const response = await apiClient.get<InterviewerResource[]>('/interviews/interviewers');
  return response.data;
}

export async function fetchMeetingRooms(): Promise<MeetingRoomResource[]> {
  const response = await apiClient.get<MeetingRoomResource[]>('/interviews/meeting-rooms');
  return response.data;
}

export async function fetchInterviews(): Promise<InterviewResource[]> {
  const response = await apiClient.get<InterviewResource[]>('/interviews');
  return response.data;
}

export async function generateInterviewSchedule(
  payload: SchedulePreviewRequest
): Promise<SchedulePreviewResponse> {
  const response = await apiClient.post<SchedulePreviewResponse>('/interviews/schedule/preview', payload);
  return response.data;
}

export const previewInterviewSchedule = generateInterviewSchedule;
