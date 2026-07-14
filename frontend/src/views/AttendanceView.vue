<template>
  <div class="p-4 md:p-8 pb-32 max-w-container-max mx-auto h-full flex flex-col overflow-y-auto">
    <LoadingState v-if="loading" message="正在读取今日考勤..." detail="正在同步当前员工的签到与签退记录" />
    <PermissionDenied v-else-if="permissionDenied" description="当前账号没有查看或操作本人考勤的权限。" />
    <ErrorState v-else-if="pageError" :message="pageError" retry-label="重新加载" @retry="loadAttendancePage" />
    <template v-else>
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
          <div class="w-[260px] h-[260px] rounded-full bg-surface-container-lowest shadow-sm flex flex-col items-center justify-center relative z-10 border border-outline-variant/20">
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
            :disabled="attendanceLoading || hasCheckedIn"
            :class="['px-8 py-4 min-w-[170px] rounded-2xl font-semibold shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 flex items-center justify-center gap-2.5 active:scale-95', 
                     hasCheckedIn ? 'bg-surface-container text-on-surface-variant opacity-40 cursor-not-allowed border border-outline-variant/30 shadow-none hover:transform-none' : 'bg-gradient-to-r from-primary to-[#2455f5] text-on-primary']"
          >
            <span class="material-symbols-outlined text-[22px]">fingerprint</span>
            <span class="text-base font-medium">{{ attendanceLoading ? '处理中...' : '签到打卡' }}</span>
          </button>
          <button 
            @click="handleCheckOut" 
            :disabled="attendanceLoading || !hasCheckedIn || hasCheckedOut"
            :class="['px-8 py-4 min-w-[170px] rounded-2xl font-semibold shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 flex items-center justify-center gap-2.5 active:scale-95', 
                     (!hasCheckedIn || hasCheckedOut) ? 'bg-surface-container text-on-surface-variant opacity-40 cursor-not-allowed border border-outline-variant/30 shadow-none hover:transform-none' : 'bg-gradient-to-r from-secondary to-[#2bb179] text-on-secondary']"
          >
            <span class="material-symbols-outlined text-[22px]">logout</span>
            <span class="text-base font-medium">{{ attendanceLoading ? '处理中...' : '签退打卡' }}</span>
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
        <!-- Today Status Card -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm overflow-hidden flex-1 flex flex-col min-h-[300px]">
          <div class="p-4 border-b border-outline-variant/30 flex items-center justify-between bg-surface-bright">
            <div class="flex items-center gap-2 text-on-surface">
              <span class="material-symbols-outlined text-primary">fact_check</span>
              <h3 class="font-title-lg text-[16px] font-semibold">今日打卡状态</h3>
            </div>
            <span class="font-label-md text-label-md text-secondary bg-secondary-container/30 px-2 py-0.5 rounded text-[10px]">数据库实时记录</span>
          </div>
          <div class="flex flex-1 flex-col justify-center gap-4 bg-surface-container-low p-6">
            <p class="text-sm text-on-surface-variant">签到时间</p>
            <strong class="text-2xl text-on-surface">{{ checkInTime || '尚未签到' }}</strong>
            <p class="text-sm text-on-surface-variant">签退时间</p>
            <strong class="text-2xl text-on-surface">{{ checkOutTime || '尚未签退' }}</strong>
          </div>
          <div class="p-4 bg-surface-container-lowest border-t border-outline-variant/30">
            <p class="font-body-md text-body-md text-on-surface font-medium">Web 打卡</p>
            <p class="font-label-md text-label-md text-outline mt-1">Sprint 1 仅记录时间事实，不进行位置验证。</p>
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

    <!-- Monthly Summary Section (New) -->
    <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm p-6 mt-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 border-b border-outline-variant/20 pb-4">
        <div>
          <h3 class="font-title-lg text-title-lg text-on-surface font-semibold flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">calendar_month</span>
            月度考勤与休假汇总
          </h3>
          <p class="text-xs text-on-surface-variant mt-1">查看选定月份的考勤状态统计、扣款/请假天数及年假剩余余额。</p>
        </div>
        <!-- Year/Month selectors and target employee selector -->
        <div class="flex flex-wrap items-center gap-3">
          <div v-if="canSelectTarget" class="flex items-center gap-2">
            <span class="text-xs font-medium text-on-surface-variant">目标员工</span>
            <select v-model="targetEmployeeId" @change="loadMonthlySummary" class="bg-surface-container-lowest border border-outline-variant rounded-lg px-3 py-1.5 text-sm outline-none focus:border-primary">
              <option v-for="emp in employees" :key="emp.id" :value="emp.id">{{ emp.full_name }} · {{ emp.department }}</option>
            </select>
          </div>
          <select v-model="selectedYear" class="bg-surface-container-lowest border border-outline-variant rounded-lg px-3 py-1.5 text-sm outline-none focus:border-primary">
            <option v-for="y in [2025, 2026, 2027]" :key="y" :value="y">{{ y }}年</option>
          </select>
          <select v-model="selectedMonth" class="bg-surface-container-lowest border border-outline-variant rounded-lg px-3 py-1.5 text-sm outline-none focus:border-primary">
            <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
          </select>
          <button @click="loadMonthlySummary" class="bg-primary text-on-primary font-semibold px-4 py-1.5 rounded-lg text-sm hover:bg-primary-container transition-all flex items-center gap-1">
            <span class="material-symbols-outlined text-sm">refresh</span>
            查询
          </button>
        </div>
      </div>

      <!-- Loading and Summary Grid -->
      <div v-if="summaryLoading" class="flex items-center justify-center py-12">
        <div class="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
      <div v-else-if="monthlySummary" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <!-- Left: Late, Early, Normal Stat Card -->
        <div class="bg-surface-container-low rounded-xl p-5 border border-outline-variant/20 flex flex-col justify-between">
          <div>
            <h4 class="text-xs font-semibold text-outline-variant uppercase tracking-wider mb-4 flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[16px] text-amber-500">warning</span>
              考勤异常与打卡统计
            </h4>
            <div class="space-y-3.5">
              <div class="flex justify-between items-center text-sm">
                <span class="text-on-surface-variant">正常打卡次数</span>
                <span class="font-semibold text-secondary bg-secondary-container/20 px-2.5 py-0.5 rounded-full text-xs">{{ monthlySummary.normal_count }} 次</span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-on-surface-variant">迟到次数 (分钟)</span>
                <span class="font-semibold" :class="monthlySummary.late_count > 0 ? 'text-amber-600 bg-amber-50 px-2.5 py-0.5 rounded-full text-xs' : 'text-on-surface-variant'">
                  {{ monthlySummary.late_count }} 次 ({{ monthlySummary.total_late_minutes }} 分钟)
                </span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-on-surface-variant">早退次数 (分钟)</span>
                <span class="font-semibold" :class="monthlySummary.early_leave_count > 0 ? 'text-amber-600 bg-amber-50 px-2.5 py-0.5 rounded-full text-xs' : 'text-on-surface-variant'">
                  {{ monthlySummary.early_leave_count }} 次 ({{ monthlySummary.total_early_leave_minutes }} 分钟)
                </span>
              </div>
            </div>
          </div>
          <div class="mt-6 text-[11px] text-outline flex items-center gap-1">
            <span class="material-symbols-outlined text-[14px]">info</span>
            正常打卡包含无异常和已获准假记录。
          </div>
        </div>

        <!-- Center: Absent, Leave Days Stat Card -->
        <div class="bg-surface-container-low rounded-xl p-5 border border-outline-variant/20 flex flex-col justify-between">
          <div>
            <h4 class="text-xs font-semibold text-outline-variant uppercase tracking-wider mb-4 flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[16px] text-red-500">cancel</span>
              缺勤与请假天数
            </h4>
            <div class="space-y-3.5">
              <div class="flex justify-between items-center text-sm">
                <span class="text-on-surface-variant">旷工/缺勤天数</span>
                <span class="font-semibold" :class="monthlySummary.absent_count > 0 ? 'text-error bg-error-container/20 px-2.5 py-0.5 rounded-full text-xs' : 'text-on-surface-variant'">
                  {{ monthlySummary.absent_count }} 天
                </span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-on-surface-variant">无薪事假天数</span>
                <span class="font-semibold" :class="monthlySummary.unpaid_leave_count > 0 ? 'text-amber-600 bg-amber-50 px-2.5 py-0.5 rounded-full text-xs' : 'text-on-surface-variant'">
                  {{ monthlySummary.unpaid_leave_count }} 天
                </span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-on-surface-variant">已休年假天数</span>
                <span class="font-semibold text-primary bg-primary/10 px-2.5 py-0.5 rounded-full text-xs">
                  {{ monthlySummary.approved_annual_leave_count }} 天
                </span>
              </div>
            </div>
          </div>
          <div class="mt-6 text-[11px] text-outline flex items-center gap-1">
            <span class="material-symbols-outlined text-[14px]">gavel</span>
            缺勤与无薪假天数将直接影响本月薪资预审。
          </div>
        </div>

        <!-- Right: Leave Balance Card -->
        <div class="bg-primary/5 rounded-xl p-5 border border-primary/10 flex flex-col justify-between relative overflow-hidden">
          <div class="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-full blur-2xl -translate-y-1/3 translate-x-1/3"></div>
          <div>
            <h4 class="text-xs font-semibold text-primary uppercase tracking-wider mb-4 flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[16px]">flight_takeoff</span>
              带薪年假查询与余额
            </h4>
            <div class="grid grid-cols-3 gap-2 mt-4 text-center">
              <div class="bg-surface-container-lowest rounded-lg p-2.5 border border-outline-variant/20 shadow-sm">
                <span class="block text-[10px] text-outline font-medium">总天数</span>
                <span class="font-display text-lg font-bold text-on-surface mt-1 block">{{ monthlySummary.total_days }}</span>
              </div>
              <div class="bg-surface-container-lowest rounded-lg p-2.5 border border-outline-variant/20 shadow-sm">
                <span class="block text-[10px] text-outline font-medium">已用</span>
                <span class="font-display text-lg font-bold text-secondary mt-1 block">{{ monthlySummary.used_days }}</span>
              </div>
              <div class="bg-surface-container-lowest rounded-lg p-2.5 border border-primary/20 shadow-sm">
                <span class="block text-[10px] text-primary font-medium">剩余</span>
                <span class="font-display text-lg font-bold text-primary mt-1 block">{{ monthlySummary.remaining_days }}</span>
              </div>
            </div>
          </div>
          <div class="mt-6 text-[11px] text-outline flex items-center gap-1">
            <span class="material-symbols-outlined text-[14px]">shield</span>
            数据受年假调休规则 and 休假申请流程保护。
          </div>
        </div>

      </div>
      <div v-else class="text-center py-12 text-on-surface-variant text-sm">
        无法获取月度汇总数据。
      </div>
    </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '../features/auth/authStore';
import { checkIn, checkOut, fetchTodayAttendance, fetchWeeklyAttendance, fetchMonthlyAttendanceSummary } from '../shared/api/modules/attendance';
import { fetchMyProfile } from '../shared/api/modules/employee';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import ErrorState from '../shared/components/feedback/ErrorState.vue';
import PermissionDenied from '../shared/components/feedback/PermissionDenied.vue';
import { ApiClientError } from '../shared/api/apiClient';

const emit = defineEmits(['show-toast']);
const { currentUser, hasAnyPermission } = useAuthStore();

const employeeName = ref('当前员工');
const loading = ref(true);
const pageError = ref('');
const permissionDenied = ref(false);
const attendanceLoading = ref(false);
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

// --- Monthly Summary & Annual Leave States ---
const selectedYear = ref(new Date().getFullYear());
const selectedMonth = ref(new Date().getMonth() + 1);
const summaryLoading = ref(false);
const monthlySummary = ref<any>(null);
const targetEmployeeId = ref<number | undefined>(undefined);
const employees = ref<any[]>([]);

const canSelectTarget = computed(() => {
  return hasAnyPermission(['payroll.all.read', 'payroll.review.read', 'audit.read', 'employee.department.read']);
});

const loadMonthlySummary = async () => {
  summaryLoading.value = true;
  try {
    const data = await fetchMonthlyAttendanceSummary(
      selectedYear.value,
      selectedMonth.value,
      targetEmployeeId.value
    );
    monthlySummary.value = data;
  } catch (err: any) {
    console.error('Failed to load monthly summary:', err);
    emit('show-toast', err.message || '加载月度汇总失败');
    monthlySummary.value = null;
  } finally {
    summaryLoading.value = false;
  }
};

const loadEmployees = async () => {
  if (!canSelectTarget.value) return;
  try {
    const { fetchEmployees } = await import('../shared/api/modules/employee');
    employees.value = await fetchEmployees();
  } catch (err) {
    console.error('Failed to load employees:', err);
  }
};

const updateClock = () => {
  const now = new Date();
  time.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
};

const fetchEmployeeName = async () => {
  const profile = await fetchMyProfile();
  employeeName.value = profile.employee.full_name || employeeName.value;
};

const formatTime = (isoString: string | null) => {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const fetchTodayStatus = async () => {
    const record = await fetchTodayAttendance();
    if (record) {
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
};

const fetchWeeklySummary = async () => {
    const records = await fetchWeeklyAttendance();
    const today = new Date();
    const monday = new Date(today);
    monday.setDate(today.getDate() - ((today.getDay() + 6) % 7));
    const recordByDate = new Map(records.map((record) => [record.attendance_date, record]));
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    weeklySummary.value = days.map((name, index) => {
      const date = new Date(monday);
      date.setDate(monday.getDate() + index);
      const key = formatLocalDate(date);
      return { name, status: recordByDate.get(key)?.status || 'NONE', isToday: key === formatLocalDate(today) };
    });
};

function formatLocalDate(value: Date) {
  return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`;
}

async function loadAttendancePage() {
  loading.value = true;
  pageError.value = '';
  permissionDenied.value = false;
  try {
    await Promise.all([fetchEmployeeName(), fetchTodayStatus(), fetchWeeklySummary()]);
  } catch (error) {
    if (error instanceof ApiClientError && error.status === 403) permissionDenied.value = true;
    else pageError.value = error instanceof Error ? error.message : '考勤数据加载失败。';
  } finally {
    loading.value = false;
  }
}

const handleCheckIn = async () => {
  if (attendanceLoading.value) return;
  attendanceLoading.value = true;
  try {
    const result = await checkIn();
    emit('show-toast', result.message || '签到成功！');
    await Promise.all([fetchTodayStatus(), fetchWeeklySummary(), loadMonthlySummary()]);
  } catch (err: any) {
    emit('show-toast', err.message || '签到失败');
  } finally {
    attendanceLoading.value = false;
  }
};

const handleCheckOut = async () => {
  if (attendanceLoading.value) return;
  attendanceLoading.value = true;
  try {
    const result = await checkOut();
    emit('show-toast', result.message || '签退成功！');
    await Promise.all([fetchTodayStatus(), fetchWeeklySummary(), loadMonthlySummary()]);
  } catch (err: any) {
    emit('show-toast', err.message || '签退失败');
  } finally {
    attendanceLoading.value = false;
  }
};

onMounted(async () => {
  updateClock();
  clockTimer = setInterval(updateClock, 1000);
  await loadAttendancePage();
  await loadEmployees();
  if (canSelectTarget.value && currentUser.value?.employee_id) {
    targetEmployeeId.value = currentUser.value.employee_id;
  }
  await loadMonthlySummary();
});

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer);
});
</script>

<style scoped>
/* 深色模式适配 */
[data-theme="dark"] .bg-amber-50 { background-color: #451a02 !important; }
[data-theme="dark"] .text-amber-600 { color: #fdba75 !important; }
[data-theme="dark"] .bg-amber-500\/20 { background-color: rgba(245, 158, 11, 0.15) !important; }
</style>
