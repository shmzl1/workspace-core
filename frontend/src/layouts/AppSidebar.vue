<template>
  <aside class="sidebar">
    <div class="sidebar__groups">
      <section v-for="group in currentGroups" :key="group.title" class="sidebar__group">
        <h2>{{ group.title }}</h2>
        <button
          v-for="item in group.items"
          :key="item"
          class="sidebar__item"
          :class="{ 'sidebar__item--active': item === activeItem }"
          @click="$emit('select', item)"
        >
          <span class="sidebar__item-mark"></span>
          {{ item }}
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

const props = defineProps<{
  activeItem: string;
  role: Role;
}>();

defineEmits<{
  select: [item: string];
  toggleRole: [];
}>();

const currentGroups = computed(() => {
  if (props.role === 'hr') {
    return [
      {
        title: '工作台',
        items: ['智能招聘看板', '候选人池', '面试日历', '招聘报告']
      },
      {
        title: '智能助手',
        items: ['智能筛选', '面试助手', '制度问答']
      },
      {
        title: '管理',
        items: ['权限审计', '系统设置']
      }
    ];
  } else {
    return [
      {
        title: '个人工作台',
        items: ['首页', '考勤签到', '假期查询', '薪资明细']
      },
      {
        title: '自助服务',
        items: ['政策中心', 'AI 助手']
      }
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
