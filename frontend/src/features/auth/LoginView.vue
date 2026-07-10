<template>
  <main class="login-page">
    <form class="login-panel" @submit.prevent="submitLogin">
      <div class="brand-mark">TF</div>
      <p class="eyebrow">TalentFlow</p>
      <h1>TalentFlow 智聘中枢</h1>
      <p class="intro">面向招聘决策、员工服务与权限审计的企业工作台。</p>

      <label>用户名<input v-model.trim="username" autocomplete="username" placeholder="请输入用户名" /></label>
      <label>密码
        <span class="password-field">
          <input v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" placeholder="请输入密码" />
          <button type="button" @click="showPassword = !showPassword">{{ showPassword ? '隐藏' : '显示' }}</button>
        </span>
      </label>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <button class="login-button" :disabled="isLoading">{{ isLoading ? '登录中...' : '登录' }}</button>

      <div class="demo-accounts">
        <p>本地演示账号，密码均为 <code>password</code></p>
        <button v-for="account in accounts" :key="account.username" type="button" @click="fillAccount(account.username)">
          {{ account.label }} · {{ account.username }}
        </button>
      </div>
    </form>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { getDefaultRoute, useAuthStore } from './authStore';

const router = useRouter();
const { login, isLoading } = useAuthStore();
const username = ref('');
const password = ref('');
const showPassword = ref(false);
const errorMessage = ref('');
const accounts = [
  { username: 'zhangwei', label: '张伟' }, { username: 'liming', label: '李明' },
  { username: 'linyuqing', label: '林雨晴' }, { username: 'wangqiang', label: '王强' },
];

function fillAccount(value: string) {
  username.value = value;
  errorMessage.value = '';
}

async function submitLogin() {
  errorMessage.value = '';
  try {
    await login(username.value, password.value);
    await router.replace(getDefaultRoute());
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '用户名或密码错误';
  }
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: grid; place-items: center; padding: 24px; background: #f4f7fb; }
.login-panel { width: min(100%, 420px); padding: 36px; border: 1px solid #dce3ef; border-radius: 8px; background: #fff; box-shadow: 0 16px 40px rgba(25, 50, 90, .1); }
.brand-mark { display: grid; width: 44px; height: 44px; place-items: center; border-radius: 8px; background: #2455f5; color: #fff; font-weight: 800; }
.eyebrow { margin: 20px 0 6px; color: #2455f5; font-size: 13px; font-weight: 800; }
h1 { margin: 0; color: #172033; font-size: 26px; } .intro { color: #64748b; line-height: 1.6; }
label { display: grid; gap: 7px; margin-top: 16px; color: #334155; font-size: 14px; font-weight: 700; }
input { width: 100%; box-sizing: border-box; padding: 11px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font: inherit; }
.password-field { display: flex; gap: 8px; } .password-field button { min-width: 52px; border: 0; background: #eef2ff; color: #2455f5; font-weight: 700; }
.login-button { width: 100%; margin-top: 22px; padding: 12px; border: 0; border-radius: 6px; background: #2455f5; color: #fff; font-weight: 800; }
.login-button:disabled { opacity: .65; } .error-message { margin: 14px 0 0; color: #b91c1c; font-size: 14px; }
.demo-accounts { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 26px; padding-top: 18px; border-top: 1px solid #e2e8f0; }
.demo-accounts p { grid-column: 1 / -1; margin: 0 0 3px; color: #64748b; font-size: 12px; } .demo-accounts button { padding: 8px; border: 1px solid #dbe4f5; border-radius: 6px; background: #fff; color: #334155; font-size: 12px; }
</style>
