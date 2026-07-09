import apiClient from '../apiClient';
import type {
  Candidate,
  CandidateApplication,
  CandidateScoreRequest,
  CandidateScoreResponse,
  Job,
  PipelineStage,
  RecruitmentReportResponse,
} from '../types';

export interface CandidateApplicationListItem extends CandidateApplication {
  candidate_name?: string | null;
  job_title?: string | null;
}

export async function fetchJobs(params?: { status?: string; department?: string }): Promise<Job[]> {
  const response = await apiClient.get<Job[]>('/recruitment/jobs', { params });
  return response.data;
}

export async function fetchJob(jobId: number): Promise<Job> {
  const response = await apiClient.get<Job>(`/recruitment/jobs/${jobId}`);
  return response.data;
}

export async function fetchCandidates(params?: {
  job_id?: number;
  stage?: PipelineStage;
  page?: number;
  page_size?: number;
}): Promise<Candidate[]> {
  const response = await apiClient.get<Candidate[]>('/recruitment/candidates', { params });
  return response.data;
}

export async function fetchApplications(): Promise<CandidateApplicationListItem[]> {
  const response = await apiClient.get<CandidateApplicationListItem[]>('/recruitment/applications');
  return response.data;
}

export async function fetchRecruitmentReport(
  params?: { time_range?: '30d' | '90d' | 'all' },
): Promise<RecruitmentReportResponse> {
  const response = await apiClient.get<RecruitmentReportResponse>('/recruitment/report', { params });
  return response.data;
}

export async function fetchApplication(applicationId: number): Promise<CandidateApplication> {
  const response = await apiClient.get<CandidateApplication>(`/recruitment/applications/${applicationId}`);
  return response.data;
}

export async function advanceStage(
  applicationId: number,
  toStage: PipelineStage,
  note?: string
): Promise<CandidateApplication> {
  const response = await apiClient.post<CandidateApplication>(
    `/recruitment/applications/${applicationId}/advance`,
    { to_stage: toStage, note }
  );
  return response.data;
}

export async function scoreCandidate(
  applicationId: number,
  payload: CandidateScoreRequest
): Promise<CandidateScoreResponse> {
  const response = await apiClient.post<CandidateScoreResponse>(
    `/recruitment/applications/${applicationId}/score`,
    payload
  );
  return response.data;
}

export const fetchCandidateScore = scoreCandidate;
