<template>
  <header class="topbar">
    <div class="topbar__brand">
      <span class="topbar__logo-mark">TF</span>
      <div>
        <strong>TalentFlow AI</strong>
        <small>智聘中枢</small>
      </div>
    </div>

    <nav class="topbar__nav" aria-label="主导航">
      <button
        v-for="item in topNavItems"
        :key="item"
        class="topbar__nav-item"
        :class="{ 'topbar__nav-item--active': item === '招聘看板' }"
      >
        {{ item }}
      </button>
    </nav>

    <div class="topbar__actions">
      <label class="topbar__search">
        <span class="topbar__search-icon"></span>
        <input placeholder="提问 AI 或搜索..." />
      </label>
      <button class="icon-button" aria-label="通知">
        <span class="icon icon--bell"></span>
      </button>
      <button class="icon-button" aria-label="最近操作">
        <span class="icon icon--history"></span>
      </button>
      <button class="icon-button" aria-label="主题切换">
        <span class="icon icon--theme"></span>
      </button>
      <div class="topbar__user">
        <span class="topbar__avatar">林</span>
        <span>林雨晴</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { topNavItems } from '../mock/recruitmentDashboard';
</script>

<style scoped lang="scss">
.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  height: var(--topbar-height);
  padding: 0 28px;
  border-bottom: 1px solid var(--color-line);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
}

.topbar__brand {
  display: flex;
  align-items: center;
  width: 240px;
  gap: 12px;
}

.topbar__logo-mark {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 11px;
  background: linear-gradient(145deg, var(--color-primary), var(--color-primary-strong));
  color: #fff;
  font-size: 14px;
  font-weight: 800;
}

.topbar__brand strong,
.topbar__brand small {
  display: block;
}

.topbar__brand strong {
  font-size: 15px;
}

.topbar__brand small {
  margin-top: 2px;
  color: var(--color-muted);
  font-size: 12px;
}

.topbar__nav {
  display: flex;
  flex: 1;
  gap: 8px;
}

.topbar__nav-item {
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-muted);
  font-size: 14px;
}

.topbar__nav-item--active {
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-weight: 700;
}

.topbar__actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar__search {
  display: flex;
  align-items: center;
  width: 230px;
  height: 40px;
  gap: 9px;
  padding: 0 12px;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: var(--color-surface-soft);
}

.topbar__search input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--color-text);
  font-size: 13px;
}

.topbar__search-icon {
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-subtle);
  border-radius: 50%;
}

.topbar__search-icon::after {
  display: block;
  width: 6px;
  height: 2px;
  margin: 9px 0 0 9px;
  transform: rotate(45deg);
  background: var(--color-subtle);
  content: '';
}

.icon-button {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 1px solid var(--color-line);
  border-radius: 50%;
  background: #fff;
}

.icon {
  position: relative;
  width: 17px;
  height: 17px;
  color: var(--color-muted);
}

.icon--bell {
  border: 2px solid currentColor;
  border-bottom: 0;
  border-radius: 9px 9px 4px 4px;
}

.icon--bell::after {
  position: absolute;
  bottom: -4px;
  left: 5px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  content: '';
}

.icon--history {
  border: 2px solid currentColor;
  border-radius: 50%;
}

.icon--history::after {
  position: absolute;
  top: 3px;
  left: 7px;
  width: 2px;
  height: 6px;
  background: currentColor;
  box-shadow: 4px 5px 0 -1px currentColor;
  content: '';
}

.icon--theme {
  border-radius: 50%;
  background: linear-gradient(90deg, currentColor 50%, transparent 50%);
  border: 2px solid currentColor;
}

.topbar__user {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text);
  font-size: 14px;
  font-weight: 700;
}

.topbar__avatar {
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  border-radius: 50%;
  background: #e9efff;
  color: var(--color-primary);
}

@media (max-width: 1180px) {
  .topbar__nav {
    display: none;
  }

  .topbar__search {
    width: 190px;
  }
}
</style>
