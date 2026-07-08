<template>
  <aside class="sidebar">
    <div class="sidebar__groups">
      <section v-for="group in currentGroups" :key="group.title" class="sidebar__group">
        <h2>{{ group.title }}</h2>
        <button
          v-for="item in group.items"
          :key="item.path"
          class="sidebar__item"
          :class="{ 'sidebar__item--active': item.path === activeRoute }"
          @click="$emit('navigate', item.id)"
        >
          <span class="sidebar__item-mark"></span>
          {{ item.label }}
        </button>
      </section>
    </div>

    <div class="sidebar__profile">
      <span class="sidebar__avatar">{{ role === 'hr' ? '林' : '张' }}</span>
      <div>
        <strong>{{ role === 'hr' ? '林雨晴' : '张伟' }}</strong>
        <small>{{ role === 'hr' ? 'HR 专员' : '高级工程师' }}</small>
      </div>
      <button aria-label="切换角色" class="sidebar__switch" @click="$emit('toggleRole')">
        <span></span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Role } from '../types';

interface SidebarItem {
  id: string;
  label: string;
  path: string;
}

const props = defineProps<{
  activeRoute: string;
  role: Role;
}>();

defineEmits<{
  navigate: [id: string];
  toggleRole: [];
}>();

const currentGroups = computed<{ title: string; items: SidebarItem[] }[]>(() => {
  if (props.role === 'hr') {
    return [
      {
        title: '工作台',
        items: [
          { id: 'dashboard', label: '智能招聘看板', path: '/hr/dashboard' },
          { id: 'candidates', label: '候选人池', path: '/hr/candidates' },
          { id: 'interviews', label: '面试日历', path: '/hr/interviews' },
          { id: 'reporting', label: '招聘报告', path: '/hr/reporting' },
        ],
      },
      {
        title: 'AI Agent',
        items: [
          { id: 'pipeline', label: '智能筛选', path: '/hr/pipeline' },
          { id: 'assistant', label: '面试助手', path: '/hr/assistant' },
          { id: 'policy', label: '制度问答', path: '/hr/policy' },
        ],
      },
      {
        title: '管理',
        items: [
          { id: 'audit', label: '权限审计', path: '/hr/audit' },
          { id: 'settings', label: '系统设置', path: '/hr/settings' },
        ],
      },
    ];
  } else {
    return [
      {
        title: '个人工作台',
        items: [
          { id: 'emp_dashboard', label: '首页', path: '/employee/dashboard' },
          { id: 'attendance', label: '考勤签到', path: '/employee/attendance' },
          { id: 'leave', label: '假期查询', path: '/employee/leave' },
          { id: 'payroll', label: '薪资明细', path: '/employee/payroll' },
        ],
      },
      {
        title: '自助服务',
        items: [
          { id: 'emp_policy', label: '政策中心', path: '/employee/policy' },
          { id: 'emp_assistant', label: 'AI 助手', path: '/employee/assistant' },
        ],
      },
    ];
  }
});
</script>

<style scoped lang="scss">
.sidebar {
  position: fixed;
  top: var(--topbar-height);
  bottom: 0;
  left: 0;
  z-index: 15;
  display: flex;
  width: var(--sidebar-width);
  flex-direction: column;
  justify-content: space-between;
  padding: 22px 16px;
  border-right: 1px solid var(--color-line);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(14px);
}

.sidebar__groups {
  display: grid;
  gap: 22px;
}

.sidebar__group h2 {
  margin: 0 0 9px 10px;
  color: var(--color-subtle);
  font-size: 12px;
  font-weight: 800;
}

.sidebar__item {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 10px;
  padding: 11px 12px;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-muted);
  text-align: left;
}

.sidebar__item-mark {
  width: 8px;
  height: 8px;
  border: 2px solid currentColor;
  border-radius: 50%;
}

.sidebar__item--active {
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-weight: 800;
}

.sidebar__profile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: #fff;
}

.sidebar__avatar {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 50%;
  background: linear-gradient(145deg, #eaf0ff, #dfe8ff);
  color: var(--color-primary);
  font-weight: 800;
}

.sidebar__profile strong,
.sidebar__profile small {
  display: block;
}

.sidebar__profile small {
  margin-top: 3px;
  color: var(--color-muted);
  font-size: 12px;
}

.sidebar__switch {
  display: grid;
  width: 30px;
  height: 30px;
  margin-left: auto;
  place-items: center;
  border-radius: 50%;
  background: var(--color-primary-soft);
}

.sidebar__switch span {
  width: 12px;
  height: 12px;
  border-top: 2px solid var(--color-primary);
  border-right: 2px solid var(--color-primary);
  transform: rotate(45deg);
}

@media (max-width: 980px) {
  .sidebar {
    position: static;
    width: auto;
    padding: 12px 18px;
  }

  .sidebar__groups {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .sidebar__profile {
    display: none;
  }
}
</style>
