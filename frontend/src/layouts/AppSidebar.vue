<template>
  <aside class="sidebar">
    <div class="sidebar__groups">
      <section v-for="group in sidebarGroups" :key="group.title" class="sidebar__group">
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
      <span class="sidebar__avatar">林</span>
      <div>
        <strong>林雨晴</strong>
        <small>HR 专员</small>
      </div>
      <button aria-label="切换角色" class="sidebar__switch">
        <span></span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { sidebarGroups } from '../mock/recruitmentDashboard';

defineProps<{
  activeItem: string;
}>();

defineEmits<{
  select: [item: string];
}>();
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
