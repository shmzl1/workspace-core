<template>
<div class="min-h-screen flex items-center justify-center relative overflow-hidden bg-surface">
      <!-- Mesh gradient background -->
      <div 
        class="absolute inset-0 z-0"
        :style="{
          background: `
            radial-gradient(circle at 15% 50%, rgba(27, 77, 255, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 85% 30%, rgba(108, 248, 187, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 50% 80%, rgba(53, 53, 196, 0.08) 0%, transparent 50%)
          `
        }"
      />
      
      <!-- Grid overlay -->
      <div 
        class="absolute inset-0 z-0 opacity-40"
        :style="{
          backgroundImage: `
            linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
          maskImage: 'radial-gradient(circle at center, black 30%, transparent 80%)',
          WebkitMaskImage: 'radial-gradient(circle at center, black 30%, transparent 80%)'
        }"
      />

      <!-- Floating Orbs -->
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-container/20 rounded-full blur-[80px] -z-10 animate-pulse mix-blend-multiply" />
      <div class="absolute bottom-1/3 right-1/4 w-96 h-96 bg-secondary-container/20 rounded-full blur-[80px] -z-10 animate-pulse mix-blend-multiply" :style="{ animationDelay: '2s' }" />

      <main class="w-full max-w-[1200px] mx-auto px-4 py-16 z-10 flex flex-col items-center relative">
        <header class="text-center mb-16">
          <h1 class="font-display text-5xl md:text-6xl font-bold tracking-tight mb-6 text-transparent bg-clip-text bg-gradient-to-br from-primary via-primary-container to-tertiary">
            TalentFlow
          </h1>
          <p class="text-2xl text-on-surface-variant font-medium mt-6">
            欢迎来到 TalentFlow 企业级智能人才管理平台
          </p>
          <p class="text-base text-outline mt-4 max-w-2xl mx-auto">
            选择您的角色，体验下一代由人工智能驱动的人力资源解决方案。
          </p>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">
          <!-- HR Role Card -->
          <button 
            @click="$emit('navigate', 'dashboard')"
            class="glass-card rounded-2xl p-10 flex flex-col items-center text-center group transition-all duration-500 hover:-translate-y-2 relative overflow-hidden text-left"
          >
            <div class="absolute inset-0 bg-gradient-to-br from-primary-container/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div class="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary-container/20 to-primary/5 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-500 shadow-inner border border-white/50">
              <span class="material-symbols-outlined text-5xl text-primary drop-shadow-sm">analytics</span>
            </div>
            <h2 class="text-2xl text-on-surface mb-4 font-bold">HR 管理门户</h2>
            <p class="text-[15px] leading-relaxed text-on-surface-variant mb-8 flex-grow max-w-[280px]">
              高效管理招聘管线、人才评估及团队数据。访问全面的分析报告和员工生命周期管理工具。
            </p>
            <div class="mt-auto w-full max-w-[240px]">
              <span class="flex items-center justify-center px-6 py-3.5 bg-primary text-white rounded-xl text-sm font-semibold group-hover:bg-primary-container group-hover:shadow-lg group-hover:shadow-primary/30 transition-all duration-300 w-full">
                进入管理门户 
                <span class="material-symbols-outlined ml-2 text-base transition-transform group-hover:translate-x-1">arrow_forward</span>
              </span>
            </div>
          </button>

          <!-- Employee Role Card -->
          <button 
            @click="$emit('navigate', 'emp_dashboard')"
            class="glass-card rounded-2xl p-10 flex flex-col items-center text-center group transition-all duration-500 hover:-translate-y-2 relative overflow-hidden text-left"
          >
            <div class="absolute inset-0 bg-gradient-to-br from-tertiary-container/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div class="w-24 h-24 rounded-2xl bg-gradient-to-br from-tertiary-container/20 to-tertiary/5 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-500 shadow-inner border border-white/50">
              <span class="material-symbols-outlined text-5xl text-tertiary drop-shadow-sm">smart_toy</span>
            </div>
            <h2 class="text-2xl text-on-surface mb-4 font-bold">员工 AI 助手</h2>
            <p class="text-[15px] leading-relaxed text-on-surface-variant mb-8 flex-grow max-w-[280px]">
              自助查询假期、薪资及公司政策。与智能助手对话，快速解决日常行政和人事问题。
            </p>
            <div class="mt-auto w-full max-w-[240px]">
              <span class="flex items-center justify-center px-6 py-3.5 bg-white/80 border-2 border-primary/20 text-primary rounded-xl text-sm font-semibold group-hover:bg-white group-hover:border-primary/40 group-hover:shadow-lg group-hover:shadow-primary/10 transition-all duration-300 w-full backdrop-blur-sm">
                <span class="font-bold mr-1.5 text-base bg-clip-text text-transparent bg-gradient-to-r from-primary-container to-tertiary">AI</span> 
                启动智能助手 
                <span class="material-symbols-outlined ml-2 text-base transition-transform group-hover:scale-110">chat_bubble</span>
              </span>
            </div>
          </button>
        </div>

        <footer class="mt-24 text-center relative z-10">
          <p class="text-sm text-outline">
            © 2024 TalentFlow 企业级人力资源管理平台。
          </p>
        </footer>
      </main>
    </div>
</template>

<script setup lang="ts">
defineEmits(['navigate']);

</script>
