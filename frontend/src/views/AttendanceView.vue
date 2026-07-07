<template>
  <div class="p-4 md:p-8 max-w-container-max mx-auto h-full flex flex-col overflow-y-auto">
    <!-- Page Header -->
    <div class="mb-6">
      <h2 class="font-headline-lg md:font-display text-headline-lg-mobile md:text-display text-on-surface tracking-tight">今日考勤</h2>
      <p class="font-body-lg text-body-lg text-on-surface-variant mt-1">早上好，张伟。准备好开始新的一天了吗？</p>
    </div>

    <!-- Main Grid Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0 mb-8">
      
      <!-- Left Panel: Clock & Action (Span 7) -->
      <div class="lg:col-span-7 bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm p-10 flex flex-col items-center justify-center relative overflow-hidden">
        <!-- Subtle AI ambient glow behind clock -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-primary-container/5 rounded-full blur-3xl pointer-events-none"></div>
        
        <!-- Large Circular Clock -->
        <div class="relative w-[300px] h-[300px] rounded-full bg-primary/5 shadow-inner flex items-center justify-center mb-10 border border-primary/10">
          <div class="absolute inset-0 rounded-full border border-primary/20 animate-[pulse_3s_cubic-bezier(0.4,0,0.6,1)_infinite]"></div>
          <div class="w-[260px] h-[260px] rounded-full bg-white shadow-sm flex flex-col items-center justify-center relative z-10 border border-outline-variant/20">
            <span class="font-label-md text-label-md text-outline uppercase tracking-widest mb-1">当前时间</span>
            <div class="font-display text-[56px] leading-none text-on-surface font-bold tabular-nums">
              {{ time }}
            </div>
            <div class="flex items-center gap-1 mt-2 text-secondary font-label-md text-label-md bg-secondary-container/20 px-3 py-1 rounded-full">
              <span class="material-symbols-outlined text-[14px]">check_circle</span> 准时
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 w-full max-w-md mx-auto relative z-10">
          <button class="flex-1 bg-gradient-to-br from-primary to-[#3535c4] text-on-primary font-headline-sm text-[16px] font-semibold py-4 rounded-lg shadow-md hover:shadow-lg transition-all transform hover:-translate-y-0.5 flex items-center justify-center gap-2">
            <span class="material-symbols-outlined">login</span> 签到
          </button>
          <button class="flex-1 bg-surface-container text-on-surface-variant font-headline-sm text-[16px] font-semibold py-4 rounded-lg border border-outline-variant/50 hover:bg-surface-container-high hover:text-on-surface transition-all flex items-center justify-center gap-2 opacity-50 cursor-not-allowed">
            <span class="material-symbols-outlined">logout</span> 签退
          </button>
        </div>
        <p class="font-body-md text-body-md text-outline mt-2 text-center relative z-10">规定签到时间：09:00 AM</p>
      </div>

      <!-- Right Panel: Location & Calendar (Span 5) -->
      <div class="lg:col-span-5 flex flex-col gap-gutter h-full">
        <!-- Location Card -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm overflow-hidden flex-1 flex flex-col min-h-[300px]">
          <div class="p-md border-b border-outline-variant/30 flex items-center justify-between bg-surface-bright">
            <div class="flex items-center gap-sm text-on-surface">
              <span class="material-symbols-outlined text-primary-container">location_on</span>
              <h3 class="font-title-lg text-[16px] font-semibold">办公地点</h3>
            </div>
            <span class="font-label-md text-label-md text-secondary bg-secondary-container/30 px-2 py-0.5 rounded text-[10px]">范围内</span>
          </div>
          
          <div class="flex-1 relative bg-surface-container-low overflow-hidden">
            <img 
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuASzfyHRoSeoH9ReWVi2DXaPr3GUUPK1Rdzhadir5zfa_AAhu1yFsZ1-WTwcrhA92N5fk76bw-5uldR62Yzhq6Pep_d8YIT_7A3z5SjVxZx-pTnPWoFa5jRVa6gglHsZ8BzfuwbF8I9Ccp3DMb09OF-W0DH_3RHv9XLz6k-F5N9LnxSIGkl9ylFhZPVCXEVI4eroREmOLMvJeayIZm-czUnq0QCgQjup4QMCcFtwPYbRRMhum8kGnzcBf6ggvgHoO4LD9LbQblrTgcE" 
              alt="Map Location" 
              class="w-full h-full object-cover opacity-80 mix-blend-multiply" 
            />
            <!-- Fake Map Pin & Radius -->
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
              <div class="w-32 h-32 bg-primary-container/20 rounded-full border border-primary-container/30 animate-pulse"></div>
              <div class="absolute w-6 h-6 bg-primary-container rounded-full shadow-lg border-2 border-white flex items-center justify-center">
                <div class="w-2 h-2 bg-white rounded-full"></div>
              </div>
            </div>
          </div>
          
          <div class="p-md bg-surface-container-lowest border-t border-outline-variant/30">
            <p class="font-body-md text-body-md text-on-surface font-medium">研发中心A栋</p>
            <p class="font-label-md text-label-md text-outline mt-1">北京市朝阳区</p>
          </div>
        </div>

        <!-- Weekly Summary / Calendar -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm p-md">
          <div class="flex items-center justify-between mb-md">
            <h3 class="font-title-lg text-[16px] font-semibold text-on-surface">本周概览</h3>
            <button class="font-label-md text-label-md text-primary-container hover:underline">查看历史</button>
          </div>
          <div class="flex justify-between items-end gap-2">
            <div class="flex flex-col items-center gap-2 flex-1">
              <div class="h-12 w-full bg-secondary-container/40 rounded-t-sm relative border-b-2 border-secondary flex items-end justify-center pb-1">
                <span class="material-symbols-outlined text-secondary text-[16px]">check</span>
              </div>
              <span class="font-label-md text-[11px] text-on-surface-variant">周一</span>
            </div>
            <div class="flex flex-col items-center gap-2 flex-1">
              <div class="h-16 w-full bg-secondary-container/40 rounded-t-sm relative border-b-2 border-secondary flex items-end justify-center pb-1">
                <span class="material-symbols-outlined text-secondary text-[16px]">check</span>
              </div>
              <span class="font-label-md text-[11px] text-on-surface-variant">周二</span>
            </div>
            <div class="flex flex-col items-center gap-2 flex-1">
              <div class="h-14 w-full bg-secondary-container/40 rounded-t-sm relative border-b-2 border-secondary flex items-end justify-center pb-1">
                <span class="material-symbols-outlined text-secondary text-[16px]">check</span>
              </div>
              <span class="font-label-md text-[11px] text-on-surface-variant">周三</span>
            </div>
            <div class="flex flex-col items-center gap-2 flex-1 relative">
              <div class="absolute -top-6 bg-primary-container text-on-primary font-label-md text-[10px] px-2 py-0.5 rounded shadow">今天</div>
              <div class="h-4 w-full bg-surface-container-high rounded-t-sm relative border-b-2 border-outline-variant flex items-end justify-center pb-1"></div>
              <span class="font-label-md text-[11px] text-primary font-bold">周四</span>
            </div>
            <div class="flex flex-col items-center gap-2 flex-1">
              <div class="h-4 w-full bg-surface-container-high rounded-t-sm relative border-b-2 border-surface-variant flex items-end justify-center pb-1"></div>
              <span class="font-label-md text-[11px] text-outline">周五</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const time = ref('');
let timer: any;

const updateClock = () => {
  const now = new Date();
  let hours = now.getHours().toString().padStart(2, '0');
  let minutes = now.getMinutes().toString().padStart(2, '0');
  time.value = `${hours}:${minutes}`;
};

onMounted(() => {
  updateClock();
  timer = setInterval(updateClock, 1000);
});

onUnmounted(() => {
  clearInterval(timer);
});
</script>
