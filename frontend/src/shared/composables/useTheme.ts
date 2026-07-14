import { ref, watch } from 'vue';

export type Theme = 'light' | 'dark';

const THEME_STORAGE_KEY = 'app-theme';

function loadTheme(): Theme {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
  } catch {
    // localStorage 不可用时忽略
  }
  return 'light';
}

function persistTheme(t: Theme) {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, t);
  } catch {
    // 忽略
  }
}

function applyHtmlTheme(t: Theme) {
  document.documentElement.setAttribute('data-theme', t);
}

/* ── 模块级单例状态 ── */
const theme = ref<Theme>(loadTheme());

/* 初始化：页面加载时立即应用到 <html>，避免 FOUC */
applyHtmlTheme(theme.value);

/* 响应式同步：theme 变化 → DOM + localStorage */
watch(theme, (t) => {
  applyHtmlTheme(t);
  persistTheme(t);
});

export function useTheme() {
  function setTheme(t: Theme) {
    theme.value = t;
  }

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark';
  }

  return {
    /** 当前主题（响应式 ref） */
    theme,
    /** 设置为 'light' 或 'dark' */
    setTheme,
    /** 在 light ↔ dark 之间切换 */
    toggleTheme,
  };
}
