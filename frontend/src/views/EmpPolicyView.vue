<template>
<div class="flex-1 p-margin-mobile md:p-margin-desktop max-w-container-max mx-auto w-full overflow-y-auto h-full">
      <!-- Hero / AI Search Section -->
      <section class="mb-12 relative">
        <div class="absolute inset-0 bg-gradient-to-b from-primary-fixed/30 to-transparent -mx-margin-mobile md:-mx-margin-desktop h-64 -z-10 pointer-events-none"></div>
        <div class="text-center max-w-3xl mx-auto pt-8 pb-10">
          <h2 class="font-headline-lg-mobile md:font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface mb-4">您好。今天需要什么帮助？</h2>
          <p class="font-body-lg text-body-lg text-on-surface-variant mb-8">即时获取公司政策、福利信息和合规文档。</p>
          
          <!-- Large AI Search Box -->
          <div class="relative max-w-2xl mx-auto rounded-2xl bg-surface-container-lowest border border-primary/20 overflow-hidden group focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-all duration-300 shadow-[0_0_20px_rgba(27,77,255,0.15)]">
            <div class="flex items-center px-4 py-3 md:py-4">
              <span class="material-symbols-outlined text-primary mr-3 animate-pulse" :style="{ fontVariationSettings: '\'FILL\' 1' }">auto_awesome</span>
              <input 
                class="flex-1 bg-transparent border-none outline-none font-body-lg text-body-lg text-on-surface placeholder-on-surface-variant/60 w-full focus:ring-0" 
                placeholder="有关福利、差旅或规章制度的问题..." 
                type="text"
              />
              <button class="ml-3 p-2 bg-primary text-on-primary rounded-lg hover:bg-primary-fixed-variant transition-colors flex items-center justify-center">
                <span class="material-symbols-outlined text-[20px]">arrow_forward</span>
              </button>
            </div>
            <div class="bg-surface-container-low px-4 py-2 border-t border-outline-variant/30 flex items-center gap-4 overflow-x-auto whitespace-nowrap">
              <span class="font-label-md text-label-md text-on-surface-variant flex items-center">
                <span class="material-symbols-outlined text-[14px] mr-1">history</span> 推荐搜索：
              </span>
              <button class="text-[13px] font-body-md text-primary hover:underline bg-primary-fixed/20 px-2 py-1 rounded cursor-pointer">产假政策</button>
              <button class="text-[13px] font-body-md text-primary hover:underline bg-primary-fixed/20 px-2 py-1 rounded cursor-pointer">远程办公指南</button>
              <button class="text-[13px] font-body-md text-primary hover:underline bg-primary-fixed/20 px-2 py-1 rounded cursor-pointer">差旅报销</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Bento Grid Layout for Content -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-gutter pb-8">
        <!-- Left Column: Categories -->
        <div class="lg:col-span-8 space-y-8">
          <h3 class="font-title-lg text-title-lg text-on-surface flex items-center">
            <span class="material-symbols-outlined mr-2 text-outline">category</span> 按类别浏览
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <!-- Category Card 1 -->
            <a class="group bg-surface-container-lowest border border-outline-variant/50 rounded-xl p-6 hover:shadow-md transition-all duration-300 relative overflow-hidden flex flex-col h-full cursor-pointer">
              <div class="absolute top-0 right-0 w-24 h-24 bg-secondary-container/20 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
              <div class="w-12 h-12 bg-secondary-container rounded-lg flex items-center justify-center mb-4 relative z-10">
                <span class="material-symbols-outlined text-on-secondary-container" :style="{ fontVariationSettings: '\'FILL\' 1' }">health_and_safety</span>
              </div>
              <h4 class="font-headline-md text-headline-md text-on-surface mb-2 relative z-10 text-[20px]">员工福利 (Benefits)</h4>
              <p class="font-body-md text-body-md text-on-surface-variant flex-1 relative z-10">医疗保险、退休计划、健康项目和员工福利。</p>
              <div class="mt-4 pt-4 border-t border-outline-variant/30 flex items-center justify-between relative z-10">
                <span class="font-label-md text-label-md text-secondary">12 篇文章</span>
                <span class="material-symbols-outlined text-outline group-hover:text-secondary group-hover:translate-x-1 transition-all">arrow_forward</span>
              </div>
            </a>
            
            <!-- Category Card 2 -->
            <a class="group bg-surface-container-lowest border border-outline-variant/50 rounded-xl p-6 hover:shadow-md transition-all duration-300 relative overflow-hidden flex flex-col h-full cursor-pointer">
              <div class="absolute top-0 right-0 w-24 h-24 bg-primary-container/10 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
              <div class="w-12 h-12 bg-primary-fixed rounded-lg flex items-center justify-center mb-4 relative z-10">
                <span class="material-symbols-outlined text-primary" :style="{ fontVariationSettings: '\'FILL\' 1' }">schedule</span>
              </div>
              <h4 class="font-headline-md text-headline-md text-on-surface mb-2 relative z-10 text-[20px]">考勤制度 (Attendance)</h4>
              <p class="font-body-md text-body-md text-on-surface-variant flex-1 relative z-10">工作时间、请假申请、法定节假日和远程办公政策。</p>
              <div class="mt-4 pt-4 border-t border-outline-variant/30 flex items-center justify-between relative z-10">
                <span class="font-label-md text-label-md text-primary">8 篇文章</span>
                <span class="material-symbols-outlined text-outline group-hover:text-primary group-hover:translate-x-1 transition-all">arrow_forward</span>
              </div>
            </a>
            
            <!-- Category Card 3 -->
            <a class="group bg-surface-container-lowest border border-outline-variant/50 rounded-xl p-6 hover:shadow-md transition-all duration-300 relative overflow-hidden flex flex-col h-full cursor-pointer">
              <div class="absolute top-0 right-0 w-24 h-24 bg-tertiary-container/10 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
              <div class="w-12 h-12 bg-tertiary-fixed rounded-lg flex items-center justify-center mb-4 relative z-10">
                <span class="material-symbols-outlined text-tertiary" :style="{ fontVariationSettings: '\'FILL\' 1' }">flight_takeoff</span>
              </div>
              <h4 class="font-headline-md text-headline-md text-on-surface mb-2 relative z-10 text-[20px]">报销流程 (Expenses)</h4>
              <p class="font-body-md text-body-md text-on-surface-variant flex-1 relative z-10">差旅津贴、公司卡、报销流程和限额。</p>
              <div class="mt-4 pt-4 border-t border-outline-variant/30 flex items-center justify-between relative z-10">
                <span class="font-label-md text-label-md text-tertiary">15 篇文章</span>
                <span class="material-symbols-outlined text-outline group-hover:text-tertiary group-hover:translate-x-1 transition-all">arrow_forward</span>
              </div>
            </a>
            
            <!-- Category Card 4 -->
            <a class="group bg-surface-container-lowest border border-outline-variant/50 rounded-xl p-6 hover:shadow-md transition-all duration-300 relative overflow-hidden flex flex-col h-full cursor-pointer">
              <div class="absolute top-0 right-0 w-24 h-24 bg-surface-variant/50 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
              <div class="w-12 h-12 bg-surface-container-highest rounded-lg flex items-center justify-center mb-4 relative z-10">
                <span class="material-symbols-outlined text-on-surface" :style="{ fontVariationSettings: '\'FILL\' 1' }">gavel</span>
              </div>
              <h4 class="font-headline-md text-headline-md text-on-surface mb-2 relative z-10 text-[20px]">行为准则 (Conduct)</h4>
              <p class="font-body-md text-body-md text-on-surface-variant flex-1 relative z-10">职业道德、保密协议、IT安全政策和职场行为规范。</p>
              <div class="mt-4 pt-4 border-t border-outline-variant/30 flex items-center justify-between relative z-10">
                <span class="font-label-md text-label-md text-on-surface">5 篇文章</span>
                <span class="material-symbols-outlined text-outline group-hover:text-on-surface group-hover:translate-x-1 transition-all">arrow_forward</span>
              </div>
            </a>
            
          </div>
        </div>

        <!-- Right Column: Hot & Required -->
        <div class="lg:col-span-4 space-y-6">
          <!-- AI Insight Card -->
          <div class="bg-gradient-to-br from-primary-container/10 to-transparent border border-primary/20 rounded-xl p-5 relative overflow-hidden">
            <div class="flex items-center mb-3">
              <span class="material-symbols-outlined text-primary mr-2" :style="{ fontVariationSettings: '\'FILL\' 1' }">lightbulb</span>
              <h3 class="font-title-lg text-title-lg text-primary text-[16px]">AI Insight</h3>
            </div>
            <p class="font-body-md text-body-md text-on-surface-variant mb-4">根据您最近的差旅申请，您可能需要查看本月生效的最新国际差旅补贴标准。</p>
            <button class="text-primary font-label-md text-label-md hover:underline flex items-center">
              查看更新 <span class="material-symbols-outlined text-[16px] ml-1">chevron_right</span>
            </button>
          </div>
          
          <!-- Required Reading -->
          <div class="bg-surface-container-lowest border border-outline-variant/50 rounded-xl p-5 shadow-sm">
            <h3 class="font-title-lg text-title-lg text-on-surface mb-4 flex items-center text-[18px]">
              <span class="material-symbols-outlined mr-2 text-error" :style="{ fontVariationSettings: '\'FILL\' 1' }">error</span>
              必读文档 (Required)
            </h3>
            <ul class="space-y-3">
              <li class="flex items-start bg-error-container/20 p-3 rounded-lg border border-error/10">
                <span class="material-symbols-outlined text-error mt-0.5 mr-3 text-[20px]">notification_important</span>
                <div>
                  <a class="font-body-lg text-body-lg text-on-surface text-[14px] font-medium hover:text-primary transition-colors block leading-tight cursor-pointer">2024 Annual Security Awareness Policy</a>
                  <span class="font-label-md text-label-md text-error text-[11px] mt-1 block">3天后截止</span>
                </div>
              </li>
              <li class="flex items-start p-2 hover:bg-surface-container-low rounded-lg transition-colors group cursor-pointer">
                <span class="material-symbols-outlined text-outline mt-0.5 mr-3 text-[20px] group-hover:text-primary">check_circle</span>
                <div>
                  <p class="font-body-lg text-body-lg text-on-surface-variant text-[14px] line-through decoration-outline/50 leading-tight">Updated WFH Guidelines Q2</p>
                  <span class="font-label-md text-label-md text-secondary text-[11px] mt-1 block">Completed</span>
                </div>
              </li>
            </ul>
          </div>
          
          <!-- Trending Policies -->
          <div class="bg-surface-container-lowest border border-outline-variant/50 rounded-xl p-5 shadow-sm">
            <h3 class="font-title-lg text-title-lg text-on-surface mb-4 flex items-center text-[18px]">
              <span class="material-symbols-outlined mr-2 text-outline">trending_up</span>
              热门浏览 (Trending)
            </h3>
            <ul class="space-y-0">
              <li class="border-b border-outline-variant/30 last:border-0">
                <a class="flex items-center justify-between py-3 group hover:px-2 transition-all duration-200 -mx-2 px-2 rounded-md hover:bg-surface-container-low cursor-pointer">
                  <div class="flex items-center min-w-0">
                    <span class="w-6 font-label-md text-label-md text-outline">01</span>
                    <span class="font-body-md text-body-md text-on-surface truncate group-hover:text-primary">2024 Public Holiday Schedule</span>
                  </div>
                  <span class="material-symbols-outlined text-[16px] text-outline opacity-0 group-hover:opacity-100 transition-opacity">north_east</span>
                </a>
              </li>
              <li class="border-b border-outline-variant/30 last:border-0">
                <a class="flex items-center justify-between py-3 group hover:px-2 transition-all duration-200 -mx-2 px-2 rounded-md hover:bg-surface-container-low cursor-pointer">
                  <div class="flex items-center min-w-0">
                    <span class="w-6 font-label-md text-label-md text-outline">02</span>
                    <span class="font-body-md text-body-md text-on-surface truncate group-hover:text-primary">IT Equipment Requisition Form</span>
                  </div>
                  <span class="material-symbols-outlined text-[16px] text-outline opacity-0 group-hover:opacity-100 transition-opacity">north_east</span>
                </a>
              </li>
              <li class="border-b border-outline-variant/30 last:border-0">
                <a class="flex items-center justify-between py-3 group hover:px-2 transition-all duration-200 -mx-2 px-2 rounded-md hover:bg-surface-container-low cursor-pointer">
                  <div class="flex items-center min-w-0">
                    <span class="w-6 font-label-md text-label-md text-outline">03</span>
                    <span class="font-body-md text-body-md text-on-surface truncate group-hover:text-primary">Annual Leave Carry-over Policy</span>
                  </div>
                  <span class="material-symbols-outlined text-[16px] text-outline opacity-0 group-hover:opacity-100 transition-opacity">north_east</span>
                </a>
              </li>
              <li class="border-b border-outline-variant/30 last:border-0">
                <a class="flex items-center justify-between py-3 group hover:px-2 transition-all duration-200 -mx-2 px-2 rounded-md hover:bg-surface-container-low cursor-pointer">
                  <div class="flex items-center min-w-0">
                    <span class="w-6 font-label-md text-label-md text-outline">04</span>
                    <span class="font-body-md text-body-md text-on-surface truncate group-hover:text-primary">Travel Expense Limits (Tier 1 Cities)</span>
                  </div>
                  <span class="material-symbols-outlined text-[16px] text-outline opacity-0 group-hover:opacity-100 transition-opacity">north_east</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
</script>
