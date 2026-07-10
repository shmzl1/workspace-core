import { computed, reactive } from 'vue';
import apiClient from '../../shared/api/apiClient';
import type { AuthUser, LoginResponse } from './authTypes';

const TOKEN_KEY = 'talentflow.token';
const USER_KEY = 'talentflow.currentUser';

const state = reactive({
  accessToken: localStorage.getItem(TOKEN_KEY) || '',
  currentUser: readCachedUser(),
  initialized: false,
  loading: false,
});

function readCachedUser(): AuthUser | null {
  try {
    const value = localStorage.getItem(USER_KEY);
    return value ? JSON.parse(value) as AuthUser : null;
  } catch {
    return null;
  }
}

function setSession(token: string, user: AuthUser) {
  state.accessToken = token;
  state.currentUser = user;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearSession() {
  state.accessToken = '';
  state.currentUser = null;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

async function login(username: string, password: string) {
  state.loading = true;
  try {
    const response = await apiClient.post<LoginResponse>('/auth/login', { username, password });
    setSession(response.data.access_token, response.data.user);
    state.initialized = true;
    return response.data.user;
  } finally {
    state.loading = false;
  }
}

async function loadCurrentUser() {
  if (!state.accessToken) {
    clearSession();
    state.initialized = true;
    return null;
  }
  state.loading = true;
  try {
    const response = await apiClient.get<AuthUser>('/auth/me');
    setSession(state.accessToken, response.data);
    return response.data;
  } catch {
    clearSession();
    return null;
  } finally {
    state.loading = false;
    state.initialized = true;
  }
}

function logout() {
  clearSession();
  state.initialized = true;
}

function hasPermission(permission: string) {
  return state.currentUser?.permissions.includes(permission) ?? false;
}

function hasAnyPermission(permissions: string[]) {
  return permissions.some(hasPermission);
}

export function getDefaultRoute() {
  if (hasPermission('recruitment.read')) return '/hr/dashboard';
  if (hasAnyPermission(['payroll.review.read', 'payroll.all.read', 'payroll.masked.read', 'payroll.department.read'])) return '/employee/payroll';
  return '/employee/dashboard';
}

export function useAuthStore() {
  return {
    state,
    currentUser: computed(() => state.currentUser),
    isAuthenticated: computed(() => Boolean(state.accessToken && state.currentUser)),
    isLoading: computed(() => state.loading),
    login,
    loadCurrentUser,
    logout,
    hasPermission,
    hasAnyPermission,
  };
}
