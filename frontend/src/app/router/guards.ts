import type { Router, RouteLocationNormalized } from 'vue-router';
import type { Role } from '../../types';

const ROLE_KEY = 'talentflow-role';

export function getSavedRole(): Role {
  return (localStorage.getItem(ROLE_KEY) as Role) || 'hr';
}

export function setSavedRole(role: Role): void {
  localStorage.setItem(ROLE_KEY, role);
}

export function getDefaultRoute(role: Role): string {
  return role === 'hr' ? '/hr/dashboard' : '/employee/dashboard';
}

export function setupGuards(router: Router): void {
  router.beforeEach((to: RouteLocationNormalized) => {
    const meta = to.meta;

    // Welcome page needs no role check
    if (to.name === 'welcome') {
      return true;
    }

    const currentRole = getSavedRole();

    // If route expects a role and user has the wrong one, redirect
    if (meta.role && meta.role !== currentRole) {
      return getDefaultRoute(currentRole);
    }

    return true;
  });
}
