<template>
  <div class="p-4 md:p-8 pb-32 max-w-container-max mx-auto h-full flex flex-col overflow-y-auto">
    <!-- Page Header -->
    <div class="mb-6">
      <h2 class="font-headline-lg md:font-display text-headline-lg-mobile md:text-display text-on-surface tracking-tight">今日考勤</h2>
      <p class="font-body-lg text-body-lg text-on-surface-variant mt-1">早上好，{{ employeeName }}。准备好开始新的一天了吗？</p>
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
              <span class="material-symbols-outlined text-[14px]">check_circle</span> 考勤追踪中
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-row justify-center gap-6 w-full max-w-md mx-auto mt-8 relative z-10">
          <button 
            @click="handleCheckIn" 
            :disabled="hasCheckedIn"
            :class="['px-8 py-4 min-w-[170px] rounded-2xl font-semibold shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 flex items-center justify-center gap-2.5 active:scale-95', 
                     hasCheckedIn ? 'bg-surface-container text-on-surface-variant opacity-40 cursor-not-allowed border border-outline-variant/30 shadow-none hover:transform-none' : 'bg-gradient-to-r from-primary to-[#2455f5] text-on-primary']"
          >
            <span class="material-symbols-outlined text-[22px]">fingerprint</span>
            <span class="text-base font-medium">签到打卡</span>
          </button>
          <button 
            @click="handleCheckOut" 
            :disabled="!hasCheckedIn || hasCheckedOut"
            :class="['px-8 py-4 min-w-[170px] rounded-2xl font-semibold shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 flex items-center justify-center gap-2.5 active:scale-95', 
                     (!hasCheckedIn || hasCheckedOut) ? 'bg-surface-container text-on-surface-variant opacity-40 cursor-not-allowed border border-outline-variant/30 shadow-none hover:transform-none' : 'bg-gradient-to-r from-secondary to-[#2bb179] text-on-secondary']"
          >
            <span class="material-symbols-outlined text-[22px]">logout</span>
            <span class="text-base font-medium">签退打卡</span>
          </button>
        </div>
        <p class="font-body-md text-body-md text-outline mt-3 text-center relative z-10">
          规定工时：09:00 - 18:00
          <span v-if="checkInTime" class="block text-primary mt-1">今日签到时间：{{ checkInTime }}</span>
          <span v-if="checkOutTime" class="block text-secondary mt-0.5">今日签退时间：{{ checkOutTime }}</span>
        </p>
      </div>

      <!-- Right Panel: Location & Calendar (Span 5) -->
      <div class="lg:col-span-5 flex flex-col gap-6 h-full">
        <!-- Location Card -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm overflow-hidden flex-1 flex flex-col min-h-[300px]">
          <div class="p-4 border-b border-outline-variant/30 flex items-center justify-between bg-surface-bright">
            <div class="flex items-center gap-2 text-on-surface">
              <span class="material-symbols-outlined text-primary">location_on</span>
              <h3 class="font-title-lg text-[16px] font-semibold">办公地点</h3>
            </div>
            <span class="font-label-md text-label-md text-secondary bg-secondary-container/30 px-2 py-0.5 rounded text-[10px]">范围匹配</span>
          </div>

          <div class="flex-1 relative bg-surface-container-low overflow-hidden">
            <img
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuASzfyHRoSeoH9ReWVi2DXaPr3GUUPK1Rdzhadir5zfa_AAhu1yFsZ1-WTwcrhA92N5fk76bw-5uldR62Yzhq6Pep_d8YIT_7A3z5SjVxZx-pTnPWoFa5jRVa6gglHsZ8BzfuwbF8I9Ccp3DMb09OF-W0DH_3RHv9XLz6k-F5N9LnxSIGkl9ylFhZPVCXEVI4eroREmOLMvJeayIZm-czUnq0QCgQjup4QMCcFtwPYbRRMhum8kGnzcBf6ggvgHoO4LD9LbQblrTgcE"
              alt="Map Location"
              class="w-full h-full object-cover opacity-80 mix-blend-multiply"
            />
            <!-- Fake Map Pin & Radius -->
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
              <div class="w-32 h-32 bg-primary/10 rounded-full border border-primary/20 animate-pulse"></div>
              <div class="absolute w-6 h-6 bg-primary rounded-full shadow-lg border-2 border-white flex items-center justify-center">
                <div class="w-2 h-2 bg-white rounded-full"></div>
              </div>
            </div>
          </div>

          <div class="p-4 bg-surface-container-lowest border-t border-outline-variant/30">
            <p class="font-body-md text-body-md text-on-surface font-medium">研发中心A栋</p>
            <p class="font-label-md text-label-md text-outline mt-1">北京市朝阳区</p>
          </div>
        </div>

        <!-- Weekly Summary / Calendar -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm p-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-title-lg text-[16px] font-semibold text-on-surface">本周概览</h3>
            <button class="font-label-md text-label-md text-primary hover:underline">查看历史</button>
          </div>
          <div class="flex justify-between items-end gap-2">
            <div v-for="(day, idx) in weeklySummary" :key="idx" class="flex flex-col items-center gap-2 flex-1 relative">
              <div v-if="day.isToday" class="absolute -top-6 bg-primary-container text-on-primary font-label-md text-[10px] px-2 py-0.5 rounded shadow">今天</div>
              <div :class="['w-full rounded-t-sm relative border-b-2 flex items-end justify-center pb-1', 
                            day.status === 'NORMAL' ? 'h-14 bg-secondary-container/40 border-secondary' : 
                            day.status === 'LATE' || day.status === 'EARLY_LEAVE' ? 'h-10 bg-amber-500/20 border-amber-500' : 
                            day.status === 'ABSENT' ? 'h-8 bg-error-container/20 border-error' : 'h-6 bg-surface-container-high border-outline-variant']">
                <span v-if="day.status === 'NORMAL'" class="material-symbols-outlined text-secondary text-[16px]">check</span>
                <span v-else-if="day.status === 'LATE'" class="material-symbols-outlined text-amber-600 text-[16px]">schedule</span>
                <span v-else-if="day.status === 'EARLY_LEAVE'" class="material-symbols-outlined text-amber-600 text-[16px]">logout</span>
                <span v-else-if="day.status === 'ABSENT'" class="material-symbols-outlined text-error text-[16px]">close</span>
              </div>
              <span :class="['font-label-md text-[11px]', day.isToday ? 'text-primary font-bold' : 'text-on-surface-variant']">{{ day.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const emit = defineEmits(['show-toast']);

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const mockHeaders = {
  'X-Mock-User-Id': '1',
  'X-Mock-Role': 'EMPLOYEE',
  'Content-Type': 'application/json'
};

const employeeName = ref('张伟');
const time = ref('');
const hasCheckedIn = ref(false);
const hasCheckedOut = ref(false);
const checkInTime = ref('');
const checkOutTime = ref('');
let clockTimer: ReturnType<typeof setInterval> | undefined;

const weeklySummary = ref([
  { name: '周一', status: 'NONE', isToday: false },
  { name: '周二', status: 'NONE', isToday: false },
  { name: '周三', status: 'NONE', isToday: false },
  { name: '周四', status: 'NONE', isToday: false },
  { name: '周五', status: 'NONE', isToday: false },
  { name: '周六', status: 'NONE', isToday: false },
  { name: '周日', status: 'NONE', isToday: false },
]);

const updateClock = () => {
  const now = new Date();
  time.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
};

const fetchEmployeeName = async () => {
  try {
    const res = await fetch(`${apiBase}/employees/me`, { headers: mockHeaders });
    const json = await res.json();
    if (json.success && json.data) {
      employeeName.value = json.data.employee.full_name;
    }
  } catch (err) {
    console.error('Failed to fetch employee profile:', err);
  }
};

const formatTime = (isoString: string | null) => {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const fetchTodayStatus = async () => {
  try {
    const res = await fetch(`${apiBase}/attendance/today`, { headers: mockHeaders });
    const json = await res.json();
    if (json.success && json.data) {
      const record = json.data;
      hasCheckedIn.value = !!record.check_in_at;
      hasCheckedOut.value = !!record.check_out_at;
      checkInTime.value = formatTime(record.check_in_at);
      checkOutTime.value = formatTime(record.check_out_at);
    } else {
      hasCheckedIn.value = false;
      hasCheckedOut.value = false;
      checkInTime.value = '';
      checkOutTime.value = '';
    }
  } catch (err) {
    console.error('Failed to fetch today attendance:', err);
  }
};

const fetchWeeklySummary = async () => {
  try {
    const res = await fetch(`${apiBase}/attendance/weekly`, { headers: mockHeaders });
    const json = await res.json();
    if (json.success && json.data) {
      const records = json.data;
      const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
      const todayDateStr = new Date().toISOString().split('T')[0];

      weeklySummary.value = records.map((r: any, idx: number) => {
        return {
          name: days[idx],
          status: r.status,
          isToday: r.attendance_date === todayDateStr
        };
      });
    }
  } catch (err) {
    console.error('Failed to fetch weekly summary:', err);
  }
};

const handleCheckIn = async () => {
  try {
    const res = await fetch(`${apiBase}/attendance/check-in`, {
      method: 'POST',
      headers: mockHeaders
    });
    const json = await res.json();
    if (json.success) {
      emit('show-toast', '签到成功！');
      await fetchTodayStatus();
      await fetchWeeklySummary();
    } else {
      emit('show-toast', json.error?.message || '签到失败');
    }
  } catch (err) {
    emit('show-toast', '网络连接失败');
  }
};

const handleCheckOut = async () => {
  try {
    const res = await fetch(`${apiBase}/attendance/check-out`, {
      method: 'POST',
      headers: mockHeaders
    });
    const json = await res.json();
    if (json.success) {
      emit('show-toast', '签退成功！');
      await fetchTodayStatus();
      await fetchWeeklySummary();
    } else {
      emit('show-toast', json.error?.message || '签退失败');
    }
  } catch (err) {
    emit('show-toast', '网络连接失败');
  }
};

onMounted(async () => {
  updateClock();
  clockTimer = setInterval(updateClock, 1000);
  await fetchEmployeeName();
  await fetchTodayStatus();
  await fetchWeeklySummary();
});

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer);
});
</script>
