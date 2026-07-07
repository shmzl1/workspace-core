<template>
<div class="pb-32 h-full">
      <!-- Page Header -->
      <div class="mb-8">
        <h2 class="font-display text-display text-on-background mb-2">政策中心</h2>
        <p class="font-body-lg text-body-lg text-on-surface-variant">在此搜索、浏览和咨询所有公司规章制度及员工福利政策。</p>
      </div>

      <!-- AI Search Hero Section -->
      <div class="mb-10 w-full max-w-4xl relative ai-gradient-border p-[2px] rounded-xl shadow-sm bg-white">
        <div class="bg-white rounded-lg p-6 flex flex-col md:flex-row items-center gap-6 relative z-10">
          <div class="w-16 h-16 rounded-full bg-primary-container/20 flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-primary text-[32px]">auto_awesome</span>
          </div>
          <div class="flex-1 w-full">
            <h3 class="font-title-lg text-title-lg text-on-background mb-1">AI 政策助手</h3>
            <p class="font-body-md text-body-md text-on-surface-variant mb-4">用自然语言提问，即刻获取相关政策解答及出处。</p>
            <div class="relative w-full">
              <input class="w-full bg-surface-container-low border border-outline-variant rounded-full py-3 pl-4 pr-12 font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" placeholder="例如：2024年的年假结转规定是什么？" type="text"/>
              <button class="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center hover:bg-primary/90 transition-colors">
                <span class="material-symbols-outlined text-[18px]">send</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Bento Grid: Categories -->
      <h3 class="font-headline-md text-headline-md text-on-background mb-4">政策分类</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter mb-10">
        <!-- Category 1 -->
        <a class="block p-6 rounded-xl bg-white border border-outline-variant shadow-sm hover:shadow-md transition-shadow hover:border-primary group" href="#">
          <div class="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center mb-4 text-primary group-hover:bg-primary group-hover:text-white transition-colors">
            <span class="material-symbols-outlined">redeem</span>
          </div>
          <h4 class="font-title-lg text-title-lg text-on-background mb-2">员工福利 (Benefit)</h4>
          <p class="font-body-md text-body-md text-on-surface-variant">医疗保险、年假、健身补贴及家庭关怀政策。</p>
        </a>
        
        <!-- Category 2 -->
        <a class="block p-6 rounded-xl bg-white border border-outline-variant shadow-sm hover:shadow-md transition-shadow hover:border-tertiary group" href="#">
          <div class="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center mb-4 text-tertiary group-hover:bg-tertiary group-hover:text-white transition-colors">
            <span class="material-symbols-outlined">schedule</span>
          </div>
          <h4 class="font-title-lg text-title-lg text-on-background mb-2">考勤休假 (Attendance)</h4>
          <p class="font-body-md text-body-md text-on-surface-variant">上下班打卡规定、加班申请流程及各类请假标准。</p>
        </a>
        
        <!-- Category 3 -->
        <a class="block p-6 rounded-xl bg-white border border-outline-variant shadow-sm hover:shadow-md transition-shadow hover:border-secondary group" href="#">
          <div class="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center mb-4 text-secondary group-hover:bg-secondary group-hover:text-white transition-colors">
            <span class="material-symbols-outlined">flight_takeoff</span>
          </div>
          <h4 class="font-title-lg text-title-lg text-on-background mb-2">差旅报销 (Travel)</h4>
          <p class="font-body-md text-body-md text-on-surface-variant">出差申请、机票酒店预订标准及费用报销指南。</p>
        </a>
        
        <!-- Category 4 -->
        <a class="block p-6 rounded-xl bg-white border border-outline-variant shadow-sm hover:shadow-md transition-shadow hover:border-error group" href="#">
          <div class="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center mb-4 text-error group-hover:bg-error group-hover:text-white transition-colors">
            <span class="material-symbols-outlined">gavel</span>
          </div>
          <h4 class="font-title-lg text-title-lg text-on-background mb-2">行为准则 (Conduct)</h4>
          <p class="font-body-md text-body-md text-on-surface-variant">商业道德、反性骚扰规定及办公场所安全规范。</p>
        </a>
      </div>

      <!-- Key Documents Section -->
      <div class="bg-white rounded-xl border border-outline-variant shadow-sm p-6 max-w-5xl mb-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="font-headline-md text-headline-md text-on-background">核心文档</h3>
          <button class="font-label-md text-label-md text-primary hover:underline">查看全部</button>
        </div>
        
        <div class="flex flex-col gap-2">
          <!-- Doc 1 -->
          <div class="flex items-center justify-between p-4 rounded-lg hover:bg-surface-container-lowest border border-transparent hover:border-outline-variant transition-colors group cursor-pointer">
            <div class="flex items-center gap-4">
              <span class="material-symbols-outlined text-outline-variant text-[28px] group-hover:text-primary transition-colors">description</span>
              <div>
                <h4 class="font-title-lg text-[16px] text-on-background">2024 员工手册 (Employee Handbook)</h4>
                <span class="font-label-md text-label-md text-on-surface-variant">最近更新: 2024年1月 • v2.1</span>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="bg-surface-container px-2 py-1 rounded font-label-md text-[11px] text-on-surface-variant uppercase tracking-wider">必读</span>
              <span class="material-symbols-outlined text-outline-variant group-hover:text-primary">download</span>
            </div>
          </div>
          
          <div class="w-full h-px bg-outline-variant/30"></div>
          
          <!-- Doc 2 -->
          <div class="flex items-center justify-between p-4 rounded-lg hover:bg-surface-container-lowest border border-transparent hover:border-outline-variant transition-colors group cursor-pointer">
            <div class="flex items-center gap-4">
              <span class="material-symbols-outlined text-outline-variant text-[28px] group-hover:text-primary transition-colors">policy</span>
              <div>
                <h4 class="font-title-lg text-[16px] text-on-background">全球商业行为与道德准则</h4>
                <span class="font-label-md text-label-md text-on-surface-variant">最近更新: 2023年11月 • v1.5</span>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-outline-variant group-hover:text-primary">download</span>
            </div>
          </div>
          
          <div class="w-full h-px bg-outline-variant/30"></div>
          
          <!-- Doc 3 -->
          <div class="flex items-center justify-between p-4 rounded-lg hover:bg-surface-container-lowest border border-transparent hover:border-outline-variant transition-colors group cursor-pointer">
            <div class="flex items-center gap-4">
              <span class="material-symbols-outlined text-outline-variant text-[28px] group-hover:text-primary transition-colors">shield_person</span>
              <div>
                <h4 class="font-title-lg text-[16px] text-on-background">数据隐私与信息安全政策</h4>
                <span class="font-label-md text-label-md text-on-surface-variant">最近更新: 2024年3月 • v3.0</span>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="bg-error-container text-on-error-container px-2 py-1 rounded font-label-md text-[11px] uppercase tracking-wider">重要</span>
              <span class="material-symbols-outlined text-outline-variant group-hover:text-primary">download</span>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
</script>
