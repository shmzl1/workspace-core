<template>
<div class="flex-1 flex flex-col md:flex-row gap-gutter h-full">
      <!-- Left Column: Balances & History (Grid) -->
      <div class="flex-1 flex flex-col gap-gutter">
        <div class="flex justify-between items-end mb-sm">
          <div>
            <h2 class="font-headline-lg text-headline-lg text-on-surface">假期管理</h2>
            <p class="font-body-md text-body-md text-on-surface-variant">查询可用额度并提交新的休假申请。</p>
          </div>
          <button class="bg-primary text-white px-md py-sm rounded-lg font-label-md text-label-md flex items-center gap-sm hover:bg-primary-fixed-variant transition-colors shadow-sm">
            <span class="material-symbols-outlined text-[18px]">add</span>
            新建申请
          </button>
        </div>
        
        <!-- Bento Grid: Leave Balances -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-md">
          <!-- Annual Leave -->
          <div class="bg-surface-container-lowest rounded-xl p-md border border-outline-variant/50 shadow-sm flex flex-col">
            <div class="flex items-center gap-sm mb-md">
              <div class="w-8 h-8 rounded-full bg-primary-container/10 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined text-[18px]">flight_takeoff</span>
              </div>
              <span class="font-title-lg text-title-lg text-on-surface">年假</span>
            </div>
            <div class="flex items-baseline gap-xs mt-auto">
              <span class="font-display text-display text-on-surface">{{ remaining('ANNUAL') }}</span>
              <span class="font-body-md text-body-md text-on-surface-variant">天剩余</span>
            </div>
            <div class="w-full bg-surface-container-highest h-1 rounded-full mt-sm overflow-hidden">
              <div class="bg-primary h-full" :style="{ width: `${percentage('ANNUAL')}%` }"></div>
            </div>
            <p class="font-label-md text-label-md text-on-surface-variant mt-sm">总额: {{ total('ANNUAL') }}天</p>
          </div>
          
          <!-- Sick Leave -->
          <div class="bg-surface-container-lowest rounded-xl p-md border border-outline-variant/50 shadow-sm flex flex-col">
            <div class="flex items-center gap-sm mb-md">
              <div class="w-8 h-8 rounded-full bg-secondary-container/10 flex items-center justify-center text-secondary">
                <span class="material-symbols-outlined text-[18px]">medical_services</span>
              </div>
              <span class="font-title-lg text-title-lg text-on-surface">带薪病假</span>
            </div>
            <div class="flex items-baseline gap-xs mt-auto">
              <span class="font-display text-display text-on-surface">{{ remaining('SICK') }}</span>
              <span class="font-body-md text-body-md text-on-surface-variant">天剩余</span>
            </div>
            <div class="w-full bg-surface-container-highest h-1 rounded-full mt-sm overflow-hidden">
              <div class="bg-secondary h-full" :style="{ width: `${percentage('SICK')}%` }"></div>
            </div>
            <p class="font-label-md text-label-md text-on-surface-variant mt-sm">总额: {{ total('SICK') }}天</p>
          </div>
          
          <!-- Time Off in Lieu -->
          <div class="bg-surface-container-lowest rounded-xl p-md border border-outline-variant/50 shadow-sm flex flex-col">
            <div class="flex items-center gap-sm mb-md">
              <div class="w-8 h-8 rounded-full bg-tertiary-container/10 flex items-center justify-center text-tertiary">
                <span class="material-symbols-outlined text-[18px]">swap_horiz</span>
              </div>
              <span class="font-title-lg text-title-lg text-on-surface">调休</span>
            </div>
            <div class="flex items-baseline gap-xs mt-auto">
              <span class="font-display text-display text-on-surface">{{ remaining('COMP_TIME') }}</span>
              <span class="font-body-md text-body-md text-on-surface-variant">小时剩余</span>
            </div>
            <div class="w-full bg-surface-container-highest h-1 rounded-full mt-sm overflow-hidden">
              <div class="bg-tertiary h-full" :style="{ width: `${percentage('COMP_TIME')}%` }"></div>
            </div>
            <p class="font-label-md text-label-md text-on-surface-variant mt-sm">总额: {{ total('COMP_TIME') }} 小时</p>
          </div>
        </div>
        
        <!-- Leave Request History List -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 shadow-sm flex-1 flex flex-col mt-sm">
          <div class="p-md border-b border-outline-variant/30 bg-surface-container-low/50 rounded-t-xl">
            <h3 class="font-title-lg text-title-lg text-on-surface">申请记录</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr>
                  <th class="px-md py-sm font-label-md text-label-md uppercase text-on-surface-variant/70 border-b border-outline-variant/30">类型</th>
                  <th class="px-md py-sm font-label-md text-label-md uppercase text-on-surface-variant/70 border-b border-outline-variant/30">时间</th>
                  <th class="px-md py-sm font-label-md text-label-md uppercase text-on-surface-variant/70 border-b border-outline-variant/30">时长</th>
                  <th class="px-md py-sm font-label-md text-label-md uppercase text-on-surface-variant/70 border-b border-outline-variant/30">状态</th>
                  <th class="px-md py-sm font-label-md text-label-md uppercase text-on-surface-variant/70 border-b border-outline-variant/30 text-right">操作</th>
                </tr>
              </thead>
              <tbody class="font-body-md text-body-md divide-y divide-outline-variant/20">
                <tr v-for="request in requests" :key="request.id" class="hover:bg-surface-container-lowest transition-colors">
                  <td class="px-md py-sm">{{ leaveLabel(request.leave_type) }}</td>
                  <td class="px-md py-sm text-on-surface-variant">{{ formatRange(request.start_at, request.end_at) }}</td>
                  <td class="px-md py-sm">{{ request.duration_hours }} 小时</td>
                  <td class="px-md py-sm"><span class="inline-flex items-center px-xs py-[2px] rounded-sm bg-secondary-container/30 text-secondary font-label-md text-[10px] uppercase">{{ request.status }}</span></td>
                  <td class="px-md py-sm text-right"><button class="text-primary hover:underline font-label-md">查看</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Column: AI Scheduling Assistant -->
      <aside class="w-full md:w-80 flex flex-col gap-md">
        <div class="bg-surface-container-lowest rounded-xl p-md border border-primary/20 shadow-sm flex flex-col h-full bg-surface-container-low/50 relative">
          <div class="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent rounded-xl pointer-events-none"></div>
          <div class="flex items-center gap-sm mb-md pb-sm border-b border-outline-variant/30 relative z-10">
            <span class="material-symbols-outlined text-primary">auto_awesome</span>
            <h3 class="font-title-lg text-title-lg text-on-surface">智能排班建议</h3>
          </div>
          <div class="flex-1 overflow-y-auto space-y-md pr-xs relative z-10">
            <!-- AI Suggestion 1 -->
            <div class="bg-surface-container-lowest p-sm rounded-lg border border-outline-variant/50 shadow-sm relative overflow-hidden">
              <div class="absolute top-0 left-0 w-1 h-full bg-primary"></div>
              <p class="font-body-md text-body-md text-on-surface mb-sm">
                下周五 (11/24) 团队中没有关键会议，且有 2 名同事已请假。建议您如果需要延长周末，可以考虑申请此日的年假。
              </p>
              <button class="w-full bg-surface-container-lowest border border-outline-variant text-primary rounded px-sm py-xs font-label-md text-label-md hover:bg-surface-container-low transition-colors">
                一键申请 11/24 年假
              </button>
            </div>
            
            <!-- AI Suggestion 2 -->
            <div class="bg-surface-container-lowest p-sm rounded-lg border border-outline-variant/50 shadow-sm relative overflow-hidden">
              <div class="absolute top-0 left-0 w-1 h-full bg-tertiary"></div>
              <p class="font-body-md text-body-md text-on-surface mb-sm">
                您的调休额度中有 8 小时将在年底过期。建议在 12 月中旬前规划使用，避免作废。
              </p>
              <button class="w-full bg-surface-container-lowest border border-outline-variant text-primary rounded px-sm py-xs font-label-md text-label-md hover:bg-surface-container-low transition-colors">
                查看合适日期
              </button>
            </div>
          </div>
          
          <!-- AI Chat Input Placeholder -->
          <div class="mt-md pt-sm border-t border-outline-variant/30 relative z-10">
            <div class="relative">
              <input class="w-full bg-surface-container-lowest border border-outline-variant rounded-[16px] pl-md pr-xl py-sm font-body-md text-body-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent h-[40px] shadow-sm" placeholder="询问排班建议..." type="text"/>
              <button class="absolute right-2 top-1/2 -translate-y-1/2 text-primary hover:text-primary-fixed-dim p-1 rounded-full">
                <span class="material-symbols-outlined text-[20px]">send</span>
              </button>
            </div>
          </div>
        </div>
      </aside>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { fetchLeaveOverview, type LeaveBalanceItem, type LeaveRequestItem } from '../shared/api/modules/employee';

const balances = ref<LeaveBalanceItem[]>([]);
const requests = ref<LeaveRequestItem[]>([]);
type LeaveType = LeaveBalanceItem['leave_type'];
const balancesByType = computed(() => new Map(balances.value.map((item) => [item.leave_type, item])));
const total = (type: LeaveType) => Number(balancesByType.value.get(type)?.total_days ?? 0);
const remaining = (type: LeaveType) => Math.max(0, total(type) - Number(balancesByType.value.get(type)?.used_days ?? 0));
const percentage = (type: LeaveType) => total(type) ? Math.round(remaining(type) * 100 / total(type)) : 0;
const leaveLabel = (type: string) => ({ ANNUAL: '年假', SICK: '带薪病假', COMP_TIME: '调休' }[type] ?? type);
const formatRange = (start: string, end: string) => `${new Date(start).toLocaleString()} 至 ${new Date(end).toLocaleString()}`;
onMounted(async () => {
  const overview = await fetchLeaveOverview();
  balances.value = overview.balances;
  requests.value = overview.requests;
});
</script>
