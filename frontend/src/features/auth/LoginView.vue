<template>
  <main class="min-h-screen flex items-center justify-center bg-[#0B1526] text-white relative overflow-hidden p-6 w-full">
    <!-- Dynamic decorative grid -->
    <div class="absolute inset-0 bg-[radial-gradient(#1B2945_1px,transparent_1px)] [background-size:24px_24px] opacity-35 z-0"></div>
    
    <!-- Neon blurred background lights -->
    <div class="absolute top-0 left-0 w-96 h-96 bg-primary/20 rounded-full blur-[120px] z-0 animate-pulse pointer-events-none"></div>
    <div class="absolute bottom-0 right-0 w-96 h-96 bg-indigo-500/15 rounded-full blur-[120px] z-0 animate-pulse pointer-events-none" style="animation-delay: 2s"></div>

    <!-- Molecular Network SVG Background -->
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] opacity-10 pointer-events-none z-0">
      <svg viewBox="0 0 200 200" class="w-full h-full animate-[spin_80s_linear_infinite] text-primary">
        <circle cx="100" cy="100" r="10" fill="none" stroke="currentColor" stroke-width="2" />
        <circle cx="50" cy="60" r="6" fill="currentColor" />
        <circle cx="150" cy="60" r="6" fill="currentColor" />
        <circle cx="50" cy="140" r="8" fill="none" stroke="currentColor" stroke-width="1.5" />
        <circle cx="150" cy="140" r="8" fill="none" stroke="currentColor" stroke-width="1.5" />
        <circle cx="100" cy="30" r="5" fill="currentColor" />
        <circle cx="100" cy="170" r="5" fill="currentColor" />
        
        <line x1="100" y1="100" x2="50" y2="60" stroke="currentColor" stroke-width="1.5" />
        <line x1="100" y1="100" x2="150" y2="60" stroke="currentColor" stroke-width="1.5" />
        <line x1="100" y1="100" x2="50" y2="140" stroke="currentColor" stroke-width="1.5" />
        <line x1="100" y1="100" x2="150" y2="140" stroke="currentColor" stroke-width="1.5" />
        <line x1="50" y1="60" x2="100" y2="30" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3" />
        <line x1="150" y1="60" x2="100" y2="30" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3" />
        <line x1="50" y1="140" x2="100" y2="170" stroke="currentColor" stroke-width="1.2" />
        <line x1="150" y1="140" x2="100" y2="170" stroke="currentColor" stroke-width="1.2" />
      </svg>
    </div>

    <!-- Centered Glassmorphism Card with Split Layout -->
    <div class="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 bg-surface/10 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl overflow-hidden relative z-10">
      
      <!-- Left side: Branding -->
      <div class="hidden md:flex flex-col justify-between p-10 md:p-12 bg-gradient-to-br from-primary/20 to-transparent border-r border-white/5 relative w-full">
        <div class="w-full">
          <div class="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shadow-lg mb-6">
            <Cpu class="w-6 h-6 text-white" />
          </div>
          <h1 class="text-3xl font-extrabold text-white tracking-tight mb-4 w-full">
            TalentFlow <br/> 智聘中枢
          </h1>
          <p class="text-sm text-blue-100/70 leading-relaxed w-full">
            大模型驱动的企业级智能人才管理与合规审计平台。为您提供严密、透明且安全的人力资源管理效率引擎。
          </p>
        </div>
        
        <div class="w-full mt-12 space-y-4">
          <div class="flex items-center gap-3 text-sm text-blue-100/80 w-full">
            <div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center shrink-0">
               <ShieldAlert class="w-4 h-4 text-primary" />
            </div>
            <span class="w-full">安全红线保障，敏感数据不挪用</span>
          </div>
          <div class="flex items-center gap-3 text-sm text-blue-100/80 w-full">
            <div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center shrink-0">
               <ArrowRight class="w-4 h-4 text-primary" />
            </div>
            <span class="w-full">多智能体协同，高效驱动业务</span>
          </div>
        </div>
      </div>

      <!-- Right side: Form -->
      <div class="p-8 md:p-12 flex flex-col justify-center bg-surface-container-lowest w-full relative">
        <div class="mb-8 w-full">
          <h2 class="text-2xl font-bold text-on-surface mb-2 w-full">欢迎回来</h2>
        </div>

        <div v-if="errorMessage" class="mb-6 p-3 bg-red-50 border border-red-100 rounded-lg text-red-600 text-xs flex items-start gap-2 w-full">
          <ShieldAlert class="w-4 h-4 shrink-0 mt-0.5" />
          <span class="w-full">{{ errorMessage }}</span>
        </div>

        <form @submit.prevent="submitLogin" class="space-y-5 w-full">
          <div class="w-full">
            <label class="block text-xs font-bold text-on-surface-variant mb-1.5 uppercase tracking-wider w-full">
              用户名
            </label>
            <div class="relative group w-full">
              <User class="w-4 h-4 text-outline absolute left-3 top-1/2 -translate-y-1/2 group-focus-within:text-primary transition-colors" />
              <input
                type="text"
                v-model.trim="username"
                placeholder="请输入用户名"
                autocomplete="username"
                required
                class="w-full h-11 pl-10 pr-4 rounded-xl border border-outline-variant/50 bg-surface-container text-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              />
            </div>
          </div>

          <div class="w-full">
            <label class="block text-xs font-bold text-on-surface-variant mb-1.5 uppercase tracking-wider w-full">
              密码
            </label>
            <div class="relative group flex items-center w-full">
              <Lock class="w-4 h-4 text-outline absolute left-3 top-1/2 -translate-y-1/2 group-focus-within:text-primary transition-colors z-10" />
              <input
                :type="showPassword ? 'text' : 'password'"
                v-model="password"
                placeholder="请输入密码"
                autocomplete="current-password"
                required
                class="w-full h-11 pl-10 pr-16 rounded-xl border border-outline-variant/50 bg-surface-container text-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              />
              <button 
                type="button" 
                @click="showPassword = !showPassword"
                class="absolute right-2 text-[10px] font-bold text-primary hover:text-primary-container px-2 py-1 rounded transition-colors"
              >
                {{ showPassword ? '隐藏' : '显示' }}
              </button>
            </div>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full h-11 mt-4 bg-primary text-white font-bold rounded-xl shadow-lg shadow-primary/20 hover:shadow-primary/30 hover:bg-primary-container hover:-translate-y-0.5 transition-all active:translate-y-0 active:scale-[0.98] disabled:opacity-65 disabled:pointer-events-none flex items-center justify-center gap-2"
          >
            <LogIn v-if="!isLoading" class="w-4 h-4 shrink-0" />
            <span>{{ isLoading ? '登录中...' : '登录' }}</span>
          </button>
        </form>

        <!-- Demo Accounts -->
        <div class="mt-8 pt-6 border-t border-outline-variant/30 w-full">
          <p class="text-[10px] text-on-surface-variant mb-4 text-center w-full">
            演示账号 (密码均为 password)
          </p>
          <div class="grid grid-cols-2 gap-3 w-full">
            <button
              v-for="account in accounts"
              :key="account.username"
              type="button"
              @click="fillAccount(account.username)"
              class="px-4 py-2.5 border border-outline-variant/40 rounded-xl bg-surface-container text-xs text-on-surface hover:border-primary/50 hover:bg-primary/5 hover:text-primary transition-colors flex items-center justify-between group cursor-pointer w-full"
            >
              <span class="font-semibold">{{ account.label }}</span>
              <span class="text-[10px] text-outline group-hover:text-primary/70">{{ account.username }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { getDefaultRoute, useAuthStore } from './authStore';
import { Cpu, User, Lock, ArrowRight, ShieldAlert, LogIn } from 'lucide-vue-next';

const router = useRouter();
const { login, isLoading } = useAuthStore();
const username = ref('');
const password = ref('');
const showPassword = ref(false);
const errorMessage = ref('');
const accounts = [
  { username: 'zhangwei', label: '张伟' }, 
  { username: 'liming', label: '李明' },
  { username: 'linyuqing', label: '林雨晴' }, 
  { username: 'wangqiang', label: '王强' },
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
