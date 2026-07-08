/**
 * 招聘模块 API
 *
 * 当前返回 mock 数据；后续只需将 mock 替换为 apiClient 调用即可接入后端。
 */
import apiClient from '../apiClient';
import type { ApiResponse, Job, CandidateSummary, CandidateApplication, PipelineStage } from '../types';

// ── 岗位 ───────────────────────────────────

export async function fetchJobs(params?: { status?: string; department?: string }): Promise<ApiResponse<Job[]>> {
  return apiClient.get('/recruitment/jobs', { params });
}

export async function fetchJob(jobId: number): Promise<ApiResponse<Job>> {
  return apiClient.get(`/recruitment/jobs/${jobId}`);
}

// ── 候选人 ─────────────────────────────────

export async function fetchCandidates(params?: {
  job_id?: number;
  stage?: PipelineStage;
  page?: number;
  page_size?: number;
}): Promise<ApiResponse<CandidateSummary[]>> {
  return apiClient.get('/recruitment/candidates', { params });
}

// ── 申请流程 ───────────────────────────────

export async function fetchApplication(applicationId: number): Promise<ApiResponse<CandidateApplication>> {
  return apiClient.get(`/recruitment/applications/${applicationId}`);
}

export async function advanceStage(applicationId: number, toStage: PipelineStage, note?: string): Promise<ApiResponse<CandidateApplication>> {
  return apiClient.post(`/recruitment/applications/${applicationId}/advance`, { to_stage: toStage, note });
}
