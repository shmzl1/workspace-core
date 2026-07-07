<template>
<div class="h-full flex flex-col pb-32 max-w-container-max mx-auto w-full flex-grow h-full overflow-y-auto">
      <!-- Welcome Header -->
      <div class="mb-lg flex justify-between items-end">
        <div>
          <h2 class="font-headline-lg text-headline-lg text-on-surface mb-xs">上午好，张伟 👋</h2>
          <p class="font-body-lg text-body-lg text-on-surface-variant">今天是 2023年10月24日，星期二。准备好开始高效的一天了吗？</p>
        </div>
        <button class="bg-primary text-white font-label-md text-label-md px-md py-sm rounded-lg hover:bg-primary-fixed-variant transition-colors flex items-center gap-xs shadow-sm">
          <span class="material-symbols-outlined text-[18px]">add</span>
          <span class="">新建申请</span>
        </button>
      </div>

      <!-- Bento Grid Layout -->
      <div class="grid grid-cols-12 gap-gutter">
        <!-- Time & Attendance Card -->
        <div class="col-span-12 md:col-span-4 glass-card rounded-xl p-md flex flex-col relative overflow-hidden bg-surface-container-lowest border border-outline-variant/30">
          <div class="absolute -right-10 -top-10 w-40 h-40 bg-secondary-container/20 rounded-full blur-2xl pointer-events-none"></div>
          <div class="flex justify-between items-start mb-md relative z-10">
            <h3 class="font-title-lg text-title-lg text-on-surface flex items-center gap-xs">
              <span class="material-symbols-outlined text-secondary">how_to_reg</span>
              今日考勤
            </h3>
            <span class="px-2 py-1 bg-secondary-container text-on-secondary-container rounded font-label-md text-[10px] uppercase">正常</span>
          </div>
          <div class="flex-grow flex flex-col justify-center items-center py-md relative z-10">
            <div class="text-4xl font-display font-light text-on-surface mb-xs">08:52</div>
            <p class="font-body-md text-body-md text-on-surface-variant mb-md">已签到 · 研发中心A栋</p>
            <button class="w-full py-3 bg-secondary text-white rounded-lg font-title-lg text-[16px] flex justify-center items-center gap-sm hover:opacity-90 transition-opacity shadow-md">
              <span class="material-symbols-outlined">fingerprint</span>
              下班打卡
            </button>
          </div>
        </div>

        <!-- Payday Countdown -->
        <div class="col-span-12 md:col-span-4 bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-md shadow-sm flex flex-col justify-between">
          <div class="flex justify-between items-start">
            <h3 class="font-title-lg text-title-lg text-on-surface flex items-center gap-xs">
              <span class="material-symbols-outlined text-tertiary">account_balance_wallet</span>
              薪资福利
            </h3>
            <button class="text-primary hover:bg-primary-container/10 p-1 rounded transition-colors">
              <span class="material-symbols-outlined text-[20px]">visibility_off</span>
            </button>
          </div>
          <div class="mt-md flex items-end gap-sm">
            <div class="font-display text-[40px] leading-none text-on-surface font-bold">12</div>
            <div class="font-body-md text-body-md text-on-surface-variant pb-1">天后发薪</div>
          </div>
          <div class="w-full bg-surface-container-high h-2 rounded-full mt-md overflow-hidden">
            <div class="bg-tertiary h-full rounded-full" :style="{ width: '60%' }"></div>
          </div>
          <div class="mt-md flex justify-between items-center pt-sm border-t border-outline-variant/30">
            <span class="font-body-md text-body-md text-on-surface-variant">上月薪资单已生成</span>
            <a class="font-label-md text-label-md text-primary flex items-center hover:underline cursor-pointer">查看详情 <span class="material-symbols-outlined text-[16px]">chevron_right</span></a>
          </div>
        </div>

        <!-- Leave Balance -->
        <div class="col-span-12 md:col-span-4 bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-md shadow-sm">
          <h3 class="font-title-lg text-title-lg text-on-surface mb-md flex items-center gap-xs">
            <span class="material-symbols-outlined text-primary">flight_takeoff</span>
            年假余额
          </h3>
          <div class="flex items-center gap-md mb-md">
            <div class="relative w-20 h-20 flex-shrink-0">
              <svg class="w-full h-full text-primary drop-shadow-sm" viewBox="0 0 36 36">
                <path class="text-surface-container-high" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="4"></path>
                <path class="text-primary" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="75, 100" strokeLinecap="round" strokeWidth="4"></path>
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="font-title-lg text-title-lg text-on-surface font-bold leading-none">12</span>
                <span class="font-label-md text-[10px] text-on-surface-variant">天</span>
              </div>
            </div>
            <div class="flex-grow space-y-xs">
              <div class="flex justify-between font-body-md text-body-md">
                <span class="text-on-surface-variant">总额度</span>
                <span class="text-on-surface font-medium">15天</span>
              </div>
              <div class="flex justify-between font-body-md text-body-md">
                <span class="text-on-surface-variant">已使用</span>
                <span class="text-on-surface font-medium">3天</span>
              </div>
            </div>
          </div>
          <div class="flex gap-sm">
            <button class="flex-1 py-2 bg-surface-container-low text-on-surface border border-outline-variant/30 rounded-lg font-label-md text-label-md hover:bg-surface-variant transition-colors">请假申请</button>
            <button class="flex-1 py-2 bg-surface-container-low text-on-surface border border-outline-variant/30 rounded-lg font-label-md text-label-md hover:bg-surface-variant transition-colors">历史记录</button>
          </div>
        </div>

        <!-- Policy Updates & Announcements -->
        <div class="col-span-12 md:col-span-8 bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-md shadow-sm">
          <div class="flex justify-between items-center mb-md pb-xs border-b border-outline-variant/30">
            <h3 class="font-title-lg text-title-lg text-on-surface flex items-center gap-xs">
              <span class="material-symbols-outlined text-on-surface-variant">campaign</span>
              通知与政策更新
            </h3>
            <a class="font-label-md text-label-md text-primary hover:underline cursor-pointer">全部查看</a>
          </div>
          <ul class="space-y-sm">
            <li class="p-sm hover:bg-surface-container-low rounded-lg transition-colors cursor-pointer group">
              <div class="flex justify-between items-start mb-1">
                <div class="flex items-center gap-xs">
                  <span class="w-2 h-2 rounded-full bg-error"></span>
                  <h4 class="font-body-md text-body-md font-medium text-on-surface group-hover:text-primary transition-colors">2024年度补充医疗保险方案升级说明</h4>
                </div>
                <span class="font-label-md text-label-md text-on-surface-variant">10-23</span>
              </div>
              <p class="font-body-md text-body-md text-on-surface-variant ml-3 line-clamp-1 text-sm">为了更好地保障员工健康，公司已全面升级补充医疗险方案，新增齿科及家属附加选项...</p>
            </li>
            <li class="p-sm hover:bg-surface-container-low rounded-lg transition-colors cursor-pointer group">
              <div class="flex justify-between items-start mb-1">
                <h4 class="font-body-md text-body-md font-medium text-on-surface group-hover:text-primary transition-colors ml-3">关于中秋国庆双节放假安排的通知</h4>
                <span class="font-label-md text-label-md text-on-surface-variant">09-20</span>
              </div>
            </li>
            <li class="p-sm hover:bg-surface-container-low rounded-lg transition-colors cursor-pointer group">
              <div class="flex justify-between items-start mb-1">
                <h4 class="font-body-md text-body-md font-medium text-on-surface group-hover:text-primary transition-colors ml-3">员工内推奖励政策更新 (V2.1)</h4>
                <span class="font-label-md text-label-md text-on-surface-variant">09-05</span>
              </div>
            </li>
          </ul>
        </div>

        <!-- Quick Actions / Tools -->
        <div class="col-span-12 md:col-span-4 bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-md shadow-sm">
          <h3 class="font-title-lg text-title-lg text-on-surface mb-md pb-xs border-b border-outline-variant/30">常用工具</h3>
          <div class="grid grid-cols-2 gap-sm">
            <button class="flex flex-col items-center justify-center p-md bg-surface-container-low rounded-lg hover:bg-primary-container/10 hover:text-primary transition-colors text-on-surface-variant">
              <span class="material-symbols-outlined mb-xs text-[28px]">description</span>
              <span class="font-label-md text-label-md">开具证明</span>
            </button>
            <button class="flex flex-col items-center justify-center p-md bg-surface-container-low rounded-lg hover:bg-primary-container/10 hover:text-primary transition-colors text-on-surface-variant">
              <span class="material-symbols-outlined mb-xs text-[28px]">medical_services</span>
              <span class="font-label-md text-label-md">健康体检</span>
            </button>
            <button class="flex flex-col items-center justify-center p-md bg-surface-container-low rounded-lg hover:bg-primary-container/10 hover:text-primary transition-colors text-on-surface-variant">
              <span class="material-symbols-outlined mb-xs text-[28px]">laptop_mac</span>
              <span class="font-label-md text-label-md">IT 支持</span>
            </button>
            <button class="flex flex-col items-center justify-center p-md bg-surface-container-low rounded-lg hover:bg-primary-container/10 hover:text-primary transition-colors text-on-surface-variant">
              <span class="material-symbols-outlined mb-xs text-[28px]">directions_bus</span>
              <span class="font-label-md text-label-md">班车查询</span>
            </button>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
</script>
