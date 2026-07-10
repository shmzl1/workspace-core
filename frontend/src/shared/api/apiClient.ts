/// <reference types="vite/client" />

import axios, { AxiosError, type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';

const configuredBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim();
export const API_BASE_URL = configuredBaseUrl || '/api/v1';
const TOKEN_KEY = 'talentflow.token';
const USER_KEY = 'talentflow.currentUser';

export function getCurrentToken(): string {
  return localStorage.getItem(TOKEN_KEY) || '';
}

export class ApiClientError extends Error {
  constructor(message: string, public readonly status?: number, public readonly code?: string) { super(message); }
}

const apiClient: AxiosInstance = axios.create({ baseURL: API_BASE_URL, timeout: 8_000, headers: { 'Content-Type': 'application/json' } });

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      if (!response.data.success) return Promise.reject(response.data.error);
      response.data = response.data.data;
    }
    return response;
  },
  (error: AxiosError<{ error?: { code?: string; message?: string } }>) => {
    const status = error.response?.status;
    const serverError = error.response?.data?.error;
    if (status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      if (window.location.pathname !== '/login') window.location.assign('/login');
    }
    const message = serverError?.message || (status === 401 ? '登录已失效，请重新登录。' : status === 403 ? '当前账号没有执行此操作的权限。' : error.request ? '网络连接失败，服务端未响应。' : error.message);
    return Promise.reject(new ApiClientError(message, status, serverError?.code));
  },
);

export default apiClient;
