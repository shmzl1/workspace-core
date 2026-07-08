import apiClient from '../apiClient';
import type { SchedulePreviewRequest, SchedulePreviewResponse } from '../types';

export async function generateInterviewSchedule(
  payload: SchedulePreviewRequest
): Promise<SchedulePreviewResponse> {
  const response = await apiClient.post<SchedulePreviewResponse>('/interviews/schedule/preview', payload);
  return response.data;
}

export const previewInterviewSchedule = generateInterviewSchedule;
