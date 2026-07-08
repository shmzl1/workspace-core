<template>
  <div class="h-full flex flex-col pb-32 max-w-container-max mx-auto w-full flex-grow h-full overflow-y-auto">
    <!-- Welcome Header -->
    <div class="mb-8 flex justify-between items-end">
      <div>
        <h2 class="font-headline-lg text-headline-lg text-on-surface mb-2">上午好，{{ employeeName }} 👋</h2>
        <p class="font-body-lg text-body-lg text-on-surface-variant">今天是 {{ formattedDate }}。准备好开始高效的一天了吗？</p>
      </div>
      <button 
        @click="emit('navigate', 'leave')"
        class="bg-primary text-white font-label-md text-label-md px-4 py-2.5 rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-1 shadow-sm"
      >
        <span class="material-symbols-outlined text-[18px]">add</span>
        <span>新建请假申请</span>
      </button>
    </div>

    <!-- Bento Grid Layout -->
    <div class="grid grid-cols-12 gap-6">
      
      <!-- Time & Attendance Card -->
      <div class="col-span-12 md:col-span-4 glass-card rounded-xl p-5 flex flex-col relative overflow-hidden bg-surface-container-lowest border border-outline-variant/30 shadow-sm">
        <div class="absolute -right-10 -top-10 w-40 h-40 bg-secondary-container/20 rounded-full blur-2xl pointer-events-none"></div>
        <div class="flex justify-between items-start mb-4 relative z-10">
          <h3 class="font-title-lg text-title-lg text-on-surface flex items-center gap-2 font-semibold">
            <span class="material-symbols-outlined text-secondary">how_to_reg</span>
            今日考勤
          </h3>
          <span :class="['px-2 py-0.5 rounded font-semibold text-[10px] uppercase', 
                         attendanceStatus === 'NORMAL' ? 'bg-emerald-50 text-emerald-700' : 
                         attendanceStatus === '未打卡' ? 'bg-surface-container text-on-surface-variant' : 'bg-amber-50 text-amber-700']">
            {{ attendanceStatus }}
          </span>
        </div>
        <div class="flex-grow flex flex-col justify-center items-center py-4 relative z-10">
          <div class="text-4xl font-display font-light text-on-surface mb-2">{{ checkInDisplayTime }}</div>
          <p class="font-body-md text-body-md text-on-surface-variant mb-4">
            {{ checkInStatusText }}
          </p>
          <button 
            @click="emit('navigate', 'attendance')"
            class="w-full py-3 bg-secondary text-white rounded-lg font-semibold text-[16px] flex justify-center items-center gap-2 hover:opacity-90 transition-opacity shadow-md"
          >
            <span class="material-symbols-outlined">fingerprint</span>
            {{ attendanceButtonText }}
          </button>
        </div>
      </div>

      <!-- Salary Summary Card -->
      <div class="col-span-12 md:col-span-4 bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-5 shadow-sm flex flex-col justify-between">
        <div class="flex justify-between items-start">
          <h3 class="font-title-lg text-title-lg text-on-surface flex items-center gap-2 font-semibold">
            <span class="material-symbols-outlined text-tertiary">account_balance_wallet</span>
            薪资福利 (摘要)
          </h3>
          <button 
            @click="toggleSalaryVisibility"
            class="text-primary hover:bg-primary-container/10 p-1 rounded transition-colors"
          >
            <span class="material-symbols-outlined text-[20px]">{{ isSalaryVisible ? 'visibility' : 'visibility_off' }}</span>
          </button>
        </div>
        <div class="mt-4 flex flex-col justify-center flex-grow">
          <div class="text-xs text-on-surface-variant mb-1 uppercase tracking-wider">本月基本应发 ({{ currency }})</div>
          <div class="font-display text-[32px] leading-none text-on-surface font-bold tracking-tight">
            {{ isSalaryVisible ? (baseSalary !== null ? '¥ ' + Number(baseSalary).toLocaleString() : '暂无数据') : '******' }}
          </div>
        </div>
        <div class="mt-4 flex justify-between items-center pt-2 border-t border-outline-variant/30 text-xs">
          <span class="font-body-md text-on-surface-variant">生效期: {{ salaryEffectiveFrom || '--' }}</span>
          <a 
            @click="emit('navigate', 'payroll')"
            class="font-label-md text-primary flex items-center hover:underline cursor-pointer font-semibold"
          >
            查看明细 <span class="material-symbols-outlined text-[16px]">chevron_right</span>
          </a>
        </div>
      </div>

      <!-- Leave Balance Card -->
      <div class="col-span-12 md:col-span-4 bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-5 shadow-sm flex flex-col justify-between">
        <h3 class="font-title-lg text-title-lg text-on-surface mb-4 flex items-center gap-2 font-semibold">
          <span class="material-symbols-outlined text-primary">flight_takeoff</span>
          年假余额
        </h3>
        <div class="flex items-center gap-4 mb-4">
          <div class="relative w-20 h-20 flex-shrink-0">
            <svg class="w-full h-full text-primary drop-shadow-sm" viewBox="0 0 36 36">
              <path class="text-surface-container-high" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-width="3"></path>
              <path class="text-primary" :d="`M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831`" fill="none" stroke="currentColor" :stroke-dasharray="`${leavePercent}, 100`" stroke-linecap="round" stroke-width="3"></path>
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span class="font-title-lg text-on-surface font-bold leading-none">{{ leaveRemaining }}</span>
              <span class="font-label-md text-[10px] text-on-surface-variant">天</span>
            </div>
          </div>
          <div class="flex-grow space-y-1 text-xs">
            <div class="flex justify-between font-body-md">
              <span class="text-on-surface-variant">总额度</span>
              <span class="text-on-surface font-medium">{{ leaveTotal }} 天</span>
            </div>
            <div class="flex justify-between font-body-md">
              <span class="text-on-surface-variant">已使用</span>
              <span class="text-on-surface font-medium">{{ leaveUsed }} 天</span>
            </div>
          </div>
        </div>
        <div class="flex gap-2 text-xs">
          <button @click="emit('navigate', 'leave')" class="flex-1 py-2 bg-surface-container-low text-on-surface border border-outline-variant/30 rounded-lg hover:bg-surface-variant transition-colors">请假历史</button>
          <button @click="emit('navigate', 'emp_policy')" class="flex-1 py-2 bg-surface-container-low text-on-surface border border-outline-variant/30 rounded-lg hover:bg-surface-variant transition-colors">制度规则</button>
        </div>
      </div>

      <!-- Policy Updates & Announcements -->
      <div class="col-span-12 md:col-span-8 bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-5 shadow-sm">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-outline-variant/30">
          <h3 class="font-title-lg text-title-lg text-on-surface flex items-center gap-2 font-semibold">
            <span class="material-symbols-outlined text-on-surface-variant">campaign</span>
            通知与政策更新
          </h3>
          <a @click="emit('navigate', 'emp_policy')" class="font-label-md text-primary hover:underline cursor-pointer font-semibold text-xs">全部查看</a>
        </div>
        <ul class="space-y-2 text-xs">
          <li @click="emit('navigate', 'emp_policy')" class="p-2 hover:bg-surface-container-low rounded-lg transition-colors cursor-pointer group">
            <div class="flex justify-between items-start mb-1">
              <div class="flex items-center gap-1">
                <span class="w-2 h-2 rounded-full bg-error"></span>
                <h4 class="font-body-md font-medium text-on-surface group-hover:text-primary transition-colors">2026年度补充医疗保险方案升级说明</h4>
              </div>
              <span class="text-on-surface-variant font-mono">07-06</span>
            </div>
            <p class="text-on-surface-variant pl-3 truncate">为了更好地保障员工健康，公司已全面升级补充医疗险方案...</p>
          </li>
          <li @click="emit('navigate', 'emp_policy')" class="p-2 hover:bg-surface-container-low rounded-lg transition-colors cursor-pointer group">
            <div class="flex justify-between items-start mb-1">
              <h4 class="font-body-md font-medium text-on-surface group-hover:text-primary transition-colors ml-3">关于中秋国庆双节放假安排的通知</h4>
              <span class="text-on-surface-variant font-mono">06-20</span>
            </div>
          </li>
        </ul>
      </div>

      <!-- Quick Actions / Tools -->
      <div class="col-span-12 md:col-span-4 bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-5 shadow-sm">
        <h3 class="font-title-lg text-title-lg text-on-surface mb-4 pb-2 border-b border-outline-variant/30 font-semibold">常用工具</h3>
        <div class="grid grid-cols-2 gap-2 text-xs">
          <button @click="emit('navigate', 'emp_assistant')" class="flex flex-col items-center justify-center p-3 bg-surface-container-low rounded-lg hover:bg-primary/5 hover:text-primary transition-colors text-on-surface-variant">
            <span class="material-symbols-outlined mb-1 text-[24px]">description</span>
            <span>开具证明</span>
          </button>
          <button @click="emit('navigate', 'emp_policy')" class="flex flex-col items-center justify-center p-3 bg-surface-container-low rounded-lg hover:bg-primary/5 hover:text-primary transition-colors text-on-surface-variant">
            <span class="material-symbols-outlined mb-1 text-[24px]">medical_services</span>
            <span>健康体检</span>
          </button>
          <button @click="emit('navigate', 'emp_assistant')" class="flex flex-col items-center justify-center p-3 bg-surface-container-low rounded-lg hover:bg-primary/5 hover:text-primary transition-colors text-on-surface-variant">
            <span class="material-symbols-outlined mb-1 text-[24px]">laptop_mac</span>
            <span>IT 支持</span>
          </button>
          <button @click="emit('navigate', 'emp_policy')" class="flex flex-col items-center justify-center p-3 bg-surface-container-low rounded-lg hover:bg-primary/5 hover:text-primary transition-colors text-on-surface-variant">
            <span class="material-symbols-outlined mb-1 text-[24px]">directions_bus</span>
            <span>班车查询</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';

const emit = defineEmits(['navigate']);

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const mockHeaders = {
  'X-Mock-User-Id': '1',
  'X-Mock-Role': 'EMPLOYEE',
  'Content-Type': 'application/json'
};

const employeeName = ref('张伟');
const isSalaryVisible = ref(false);

const baseSalary = ref<number | null>(null);
const currency = ref('CNY');
const salaryEffectiveFrom = ref('');

const leaveTotal = ref(15);
const leaveUsed = ref(3);
const leaveRemaining = computed(() => {
  const rem = leaveTotal.value - leaveUsed.value;
  return rem >= 0 ? rem : 0;
});
const leavePercent = computed(() => {
  if (leaveTotal.value <= 0) return 0;
  return Math.round((leaveRemaining.value / leaveTotal.value) * 100);
});

const attendanceStatus = ref('未打卡');
const checkInDisplayTime = ref('--:--');
const checkInStatusText = ref('今日尚未开始工作打卡');
const attendanceButtonText = ref('去考勤打卡');

const formattedDate = computed(() => {
  const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  const date = now.getDate();
  const dayName = days[now.getDay()];
  return `${year}年${month}月${date}日，${dayName}`;
});

const toggleSalaryVisibility = () => {
  isSalaryVisible.value = !isSalaryVisible.value;
};

const formatTime = (isoString: string | null) => {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const fetchDashboardData = async () => {
  try {
    // 1. Fetch Employee and Leave Balance
    const empRes = await fetch(`${apiBase}/employees/me`, { headers: mockHeaders });
    const empJson = await empRes.json();
    if (empJson.success && empJson.data) {
      const data = empJson.data;
      employeeName.value = data.employee.full_name;
      if (data.leave_balance) {
        leaveTotal.value = Number(data.leave_balance.total_days);
        leaveUsed.value = Number(data.leave_balance.used_days);
      }
    }

    // 2. Fetch today's attendance status
    const attRes = await fetch(`${apiBase}/attendance/today`, { headers: mockHeaders });
    const attJson = await attRes.json();
    if (attJson.success && attJson.data) {
      const record = attJson.data;
      if (record.check_in_at) {
        checkInDisplayTime.value = formatTime(record.check_in_at);
        attendanceStatus.value = record.status;
        checkInStatusText.value = `已签到 · 研发中心A栋`;
        attendanceButtonText.value = record.check_out_at ? '已打卡结束' : '去签退打卡';
      }
    }

    // 3. Fetch salary summary
    const salRes = await fetch(`${apiBase}/payroll/me`, { headers: mockHeaders });
    const salJson = await salRes.json();
    if (salJson.success && salJson.data) {
      baseSalary.value = salJson.data.base_salary;
      currency.value = salJson.data.currency || 'CNY';
      salaryEffectiveFrom.value = salJson.data.effective_from || '';
    }
  } catch (err) {
    console.error('Failed to fetch dashboard widgets data:', err);
  }
};

onMounted(async () => {
  await fetchDashboardData();
});
</script>
