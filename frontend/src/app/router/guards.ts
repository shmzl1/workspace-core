import type { Router } from 'vue-router';
import { getDefaultRoute, useAuthStore } from '../../features/auth/authStore';

export function setupGuards(router: Router): void {
  router.beforeEach(async (to) => {
    const auth = useAuthStore();
    if (!auth.state.initialized) await auth.loadCurrentUser();
    if (to.name === 'login') return auth.isAuthenticated.value ? getDefaultRoute() : true;
    if (to.meta.requiresAuth && !auth.isAuthenticated.value) return { name: 'login' };
    const required = to.meta.anyPermissions || [];
    if (required.length && !auth.hasAnyPermission(required)) return getDefaultRoute();
    return true;
  });
}
