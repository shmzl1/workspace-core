/**
 * Axios 实例与通用拦截器
 */
/// <reference types="vite/client" />

import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios';

const configuredBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim();
const BASE_URL = configuredBaseUrl || '/api/v1';
if (import.meta.env.DEV && !configuredBaseUrl) {
  console.warn('[API] VITE_API_BASE_URL 未配置，当前通过 Vite /api 代理访问后端。');
}
const DEV_IDENTITY_KEY = 'talentflow.devIdentity';

export interface DevIdentity {
  userId: number;
  role: 'EMPLOYEE' | 'DEPARTMENT_MANAGER' | 'HR_SPECIALIST' | 'PAYROLL_ADMIN';
}

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
    public readonly code?: string,
  ) {
    super(message);
  }
}

export function getDevIdentity(): DevIdentity {
  const fallback: DevIdentity = { userId: 1, role: 'EMPLOYEE' };
  if (!import.meta.env.DEV) return fallback;
  try {
    return { ...fallback, ...JSON.parse(localStorage.getItem(DEV_IDENTITY_KEY) || '{}') };
  } catch {
    return fallback;
  }
}

export function setDevIdentity(identity: DevIdentity): void {
  localStorage.setItem(DEV_IDENTITY_KEY, JSON.stringify(identity));
}

const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 8_000,
  headers: { 'Content-Type': 'application/json' },
});

// ── 请求拦截器 ──────────────────────────────
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('talentflow.token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  } else if (import.meta.env.DEV) {
    const identity = getDevIdentity();
    config.headers['X-Mock-User-Id'] = String(identity.userId);
    config.headers['X-Mock-Role'] = identity.role;
  }
  return config;
});

// ── 响应拦截器 ──────────────────────────────
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 统一提取 data 层
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      if (!response.data.success) {
        console.warn('[API] 业务错误:', response.data.error);
        return Promise.reject(response.data.error);
      }
      // 将 data 提升为 response.data，方便调用方直接使用
      response.data = response.data.data;
    }
    return response;
  },
  (error: AxiosError<{ error?: { code?: string; message?: string } }>) => {
    // 统一处理 HTTP 层错误
    if (error.response) {
      const { status } = error.response;
      if (status === 401) {
        console.warn('[API] 未认证，请重新登录');
      } else if (status === 403) {
        console.warn('[API] 权限不足');
      } else if (status >= 500) {
        console.error('[API] 服务器错误:', status);
      }
    } else if (error.request) {
      console.error('[API] 网络错误：无响应');
    }
    const status = error.response?.status;
    const serverError = error.response?.data?.error;
    const message = serverError?.message || (
      status === 401 ? '未登录或身份无效。'
        : status === 403 ? '当前账号无权执行此操作。'
          : status && status >= 500 ? '服务端处理失败，请稍后重试。'
            : error.request ? '网络连接失败，服务端未响应。'
              : error.message
    );
    return Promise.reject(new ApiClientError(message, status, serverError?.code));
  }
);

export default apiClient;
