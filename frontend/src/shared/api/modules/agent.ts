import apiClient, { API_BASE_URL, ApiClientError, getCurrentToken } from '../apiClient';
import type {
  AgentEvent,
  RecruitmentRunRequest,
  RecruitmentRunSnapshot,
} from '../../agent/contracts';

const TOKEN_KEY = 'talentflow.token';
const USER_KEY = 'talentflow.currentUser';

export interface AgentEventStreamCallbacks {
  onEvent: (event: AgentEvent) => void;
  onOpen?: () => void;
  onComplete?: () => void;
  onError?: (error: Error) => void;
}

export async function createRecruitmentRun(
  payload: RecruitmentRunRequest,
): Promise<RecruitmentRunSnapshot> {
  const response = await apiClient.post<RecruitmentRunSnapshot>('/agent/recruitment/runs', payload);
  return response.data;
}

export async function getRecruitmentRun(runId: string): Promise<RecruitmentRunSnapshot> {
  const response = await apiClient.get<RecruitmentRunSnapshot>(`/agent/recruitment/runs/${encodeURIComponent(runId)}`);
  return response.data;
}

export async function approveJobMatchReview(
  runId: string,
): Promise<RecruitmentRunSnapshot> {
  const response = await apiClient.post<RecruitmentRunSnapshot>(
    `/agent/recruitment/runs/${encodeURIComponent(runId)}/approve-job-match-review`,
  );
  return response.data;
}

export async function approveDecisionReview(
  runId: string,
): Promise<RecruitmentRunSnapshot> {
  const response = await apiClient.post<RecruitmentRunSnapshot>(
    `/agent/recruitment/runs/${encodeURIComponent(runId)}/approve-decision-review`,
  );
  return response.data;
}

export async function subscribeRecruitmentRunEvents(
  runId: string,
  callbacks: AgentEventStreamCallbacks,
  signal: AbortSignal,
): Promise<void> {
  const token = getCurrentToken();
  if (!token) throw new ApiClientError('登录状态已失效，请重新登录。', 401, 'TOKEN_INVALID');
  const seenEventIds = new Set<string>();
  let response: Response;
  try {
    response = await fetch(buildApiUrl(`/agent/recruitment/runs/${encodeURIComponent(runId)}/events`), {
      method: 'GET',
      headers: {
        Accept: 'text/event-stream',
        Authorization: `Bearer ${token}`,
      },
      cache: 'no-store',
      signal,
    });
  } catch (cause) {
    if (signal.aborted) return;
    const error = new ApiClientError('实时事件连接失败，请检查后端服务和网络。');
    callbacks.onError?.(error);
    throw cause instanceof Error ? error : new Error(error.message);
  }

  if (!response.ok) {
    const error = await readStreamError(response);
    if (response.status === 401) clearSessionAndRedirect();
    callbacks.onError?.(error);
    throw error;
  }
  if (!response.body) {
    const error = new ApiClientError('浏览器未提供可读取的实时事件流。');
    callbacks.onError?.(error);
    throw error;
  }

  callbacks.onOpen?.();
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  try {
    while (!signal.aborted) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, '\n');
      let boundary = buffer.indexOf('\n\n');
      while (boundary >= 0) {
        const block = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        emitSseBlock(block, seenEventIds, callbacks);
        boundary = buffer.indexOf('\n\n');
      }
    }
    callbacks.onComplete?.();
  } catch (cause) {
    if (signal.aborted) return;
    const error = new ApiClientError('实时事件连接已中断，请刷新页面恢复本次运行。');
    callbacks.onError?.(error);
    throw cause instanceof Error ? error : new Error(error.message);
  } finally {
    reader.releaseLock();
  }
}

function emitSseBlock(
  block: string,
  seenEventIds: Set<string>,
  callbacks: AgentEventStreamCallbacks,
): void {
  if (!block.trim() || block.startsWith(':')) return;
  let id = '';
  let eventName = 'message';
  const dataLines: string[] = [];
  for (const line of block.split('\n')) {
    if (line.startsWith('id:')) id = line.slice(3).trim();
    else if (line.startsWith('event:')) eventName = line.slice(6).trim();
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trimStart());
  }
  if (eventName !== 'agent_event' || dataLines.length === 0) return;
  const parsed = JSON.parse(dataLines.join('\n')) as AgentEvent;
  const eventId = parsed.event_id || id;
  if (!eventId || seenEventIds.has(eventId)) return;
  seenEventIds.add(eventId);
  callbacks.onEvent(parsed);
}

function buildApiUrl(path: string): string {
  const base = API_BASE_URL.replace(/\/$/, '');
  return new URL(`${base}${path}`, window.location.origin).toString();
}

async function readStreamError(response: Response): Promise<ApiClientError> {
  try {
    const payload = await response.json() as { error?: { code?: string; message?: string } };
    return new ApiClientError(
      payload.error?.message || `实时事件请求失败（${response.status}）。`,
      response.status,
      payload.error?.code,
    );
  } catch {
    return new ApiClientError(`实时事件请求失败（${response.status}）。`, response.status);
  }
}

function clearSessionAndRedirect(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  if (window.location.pathname !== '/login') window.location.assign('/login');
}

