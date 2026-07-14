<template>
  <AppShell />
</template>

<script setup lang="ts">
import AppShell from './layouts/AppShell.vue';
import { useTheme } from './shared/composables/useTheme';

/* 挂载时应用持久化主题（composable 内部已做模块级初始化，此处确保副作用生效） */
useTheme();
</script>
