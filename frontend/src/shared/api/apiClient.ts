/**
 * Axios 实例与通用拦截器
 */
/// <reference types="vite/client" />

import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL as string || '/api/v1';

const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
});

// ── 请求拦截器 ──────────────────────────────
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // 后续接入认证后在此注入 token
  // const token = getAuthToken();
  // if (token) config.headers.Authorization = `Bearer ${token}`;
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
  (error) => {
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
    return Promise.reject(error);
  }
);

export default apiClient;
