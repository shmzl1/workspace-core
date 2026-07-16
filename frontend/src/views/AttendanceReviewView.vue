<template>
  <div class="p-4 md:p-8 pb-32 max-w-container-max mx-auto h-full flex flex-col overflow-y-auto">
    <!-- Header -->
    <div class="mb-6">
      <h2 class="font-headline-lg md:font-display text-headline-lg-mobile md:text-display text-on-surface tracking-tight">考勤审查</h2>
      <p class="font-body-lg text-body-lg text-on-surface-variant mt-1">
        按当前授权范围查看员工考勤记录与月度汇总。
      </p>
    </div>

    <!-- Filter Panel -->
    <div class="bg-primary/5 rounded-xl border border-primary/20 p-5 mb-6">
      <h3 class="font-title-lg text-[16px] font-semibold text-primary mb-3 flex items-center gap-2">
        <span class="material-symbols-outlined text-[20px]">tune</span>
        考勤查询范围
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div>
          <span class="block text-xs font-medium text-on-surface-variant mb-1">当前访问角色</span>
          <p class="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2.5 text-sm font-semibold text-on-surface">
            {{ currentRoleLabel }}
          </p>
        </div>
        <div v-if="canSelectTarget">
          <label class="block text-xs font-medium text-on-surface-variant mb-1">查询目标员工</label>
          <select v-model.number="targetEmployeeId" class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2.5 text-sm outline-none focus:border-primary">
            <option v-for="employee in filteredEmployees" :key="employee.id" :value="employee.id">{{ employee.full_name }} · {{ employee.department }}</option>
          </select>
        </div>
        <div v-else>
          <span class="block text-xs font-medium text-on-surface-variant mb-1">查询员工</span>
          <p class="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2.5 text-sm text-on-surface">
            {{ currentUser?.full_name || '—' }}
          </p>
        </div>
        <!-- Period type selector -->
        <div class="flex items-end gap-2">
          <div class="flex-1">
            <span class="block text-xs font-medium text-on-surface-variant mb-1">查询时段</span>
            <div class="flex rounded-lg border border-outline-variant overflow-hidden">
              <button
                v-for="pt in periodTypes"
                :key="pt.value"
                @click="periodType = pt.value"
                :class="['flex-1 py-2 text-xs font-semibold transition-colors', periodType === pt.value ? 'bg-primary text-on-primary' : 'bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container-low']"
              >{{ pt.label }}</button>
            </div>
          </div>
          <button
            @click="fetchReview"
            :disabled="loading"
            class="bg-primary text-on-primary font-semibold py-2.5 px-4 rounded-lg text-sm hover:bg-primary-container transition-all flex items-center gap-1 whitespace-nowrap"
          >
            <span class="material-symbols-outlined text-sm">search</span>
            {{ loading ? '查询中……' : '查询' }}
          </button>
        </div>
        <!-- Date/Month pickers -->
        <div v-if="periodType === 'date'" class="md:col-span-1">
          <label class="block text-xs font-medium text-on-surface-variant mb-1">指定日期</label>
          <input type="date" v-model="reviewDate" class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2.5 text-sm outline-none focus:border-primary" />
        </div>
        <div v-if="periodType === 'month'" class="md:col-span-1 flex gap-2">
          <div class="flex-1">
            <label class="block text-xs font-medium text-on-surface-variant mb-1">年份</label>
            <select v-model.number="selectedYear" class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2.5 text-sm outline-none focus:border-primary">
              <option v-for="y in [2025, 2026, 2027]" :key="y" :value="y">{{ y }}年</option>
            </select>
          </div>
          <div class="flex-1">
            <label class="block text-xs font-medium text-on-surface-variant mb-1">月份</label>
            <select v-model.number="selectedMonth" class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2.5 text-sm outline-none focus:border-primary">
              <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <LoadingState v-if="initialLoading" message="正在读取考勤信息..." detail="正在进行权限校验并拉取考勤数据" />

    <!-- Access Denied -->
    <div v-else-if="accessError" class="bg-error-container/20 border border-error/30 rounded-xl p-8 text-center flex flex-col items-center justify-center mb-8">
      <div class="w-16 h-16 rounded-full bg-error/10 flex items-center justify-center text-error mb-4">
        <span class="material-symbols-outlined text-[36px]">gpp_bad</span>
      </div>
      <h3 class="font-headline-sm text-on-surface font-semibold mb-2">访问被拒绝 (Access Denied)</h3>
      <p class="text-sm text-on-surface-variant max-w-md leading-relaxed">{{ accessError }}</p>
    </div>

    <!-- Service Error -->
    <ErrorState
      v-else-if="serviceError"
      title="考勤数据暂时无法获取"
      :message="serviceError"
      retry-label="重新查询"
      @retry="fetchReview"
    />

    <!-- Results -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
      <!-- Main data -->
      <div class="lg:col-span-8 flex flex-col gap-6">
        <!-- Employee Info Card -->
        <div v-if="reviewData" class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-6 shadow-sm">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-lg">
              {{ (reviewData.employee_name || '?').slice(0, 1) }}
            </div>
            <div>
              <h3 class="font-title-lg text-on-surface font-semibold">{{ reviewData.employee_name }}</h3>
              <p class="text-sm text-on-surface-variant">{{ reviewData.employee_department }} · {{ reviewData.employee_job_title }}</p>
            </div>
          </div>
        </div>

        <!-- Daily View: Specific Date -->
        <div v-if="periodType === 'date'" class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-6 shadow-sm">
          <h3 class="font-title-lg text-on-surface font-semibold mb-4">
            {{ reviewDate }} 考勤记录
          </h3>
          <div v-if="reviewData?.record" class="space-y-4">
            <!-- Time Card -->
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-surface-container-low rounded-xl p-4 text-center">
                <p class="text-xs text-on-surface-variant mb-1">上班打卡</p>
                <p class="text-xl font-bold text-on-surface">{{ formatTime(reviewData.record.check_in_at) }}</p>
              </div>
              <div class="bg-surface-container-low rounded-xl p-4 text-center">
                <p class="text-xs text-on-surface-variant mb-1">下班打卡</p>
                <p class="text-xl font-bold text-on-surface">{{ formatTime(reviewData.record.check_out_at) }}</p>
              </div>
            </div>
            <!-- Status + Details -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div class="bg-surface-container-low rounded-lg p-3 text-center">
                <p class="text-xs text-on-surface-variant mb-0.5">考勤状态</p>
                <p :class="['text-sm font-bold', statusColor(reviewData.record.status)]">{{ statusLabel(reviewData.record.status) }}</p>
              </div>
              <div class="bg-surface-container-low rounded-lg p-3 text-center">
                <p class="text-xs text-on-surface-variant mb-0.5">迟到分钟</p>
                <p class="text-sm font-bold text-on-surface">{{ reviewData.record.late_minutes }} 分钟</p>
              </div>
              <div class="bg-surface-container-low rounded-lg p-3 text-center">
                <p class="text-xs text-on-surface-variant mb-0.5">早退分钟</p>
                <p class="text-sm font-bold text-on-surface">{{ reviewData.record.early_leave_minutes }} 分钟</p>
              </div>
              <div class="bg-surface-container-low rounded-lg p-3 text-center">
                <p class="text-xs text-on-surface-variant mb-0.5">签到来源</p>
                <p class="text-sm font-bold text-on-surface">{{ reviewData.record.source }}</p>
              </div>
            </div>
          </div>
          <!-- No record -->
          <div v-else class="text-center py-8">
            <span class="material-symbols-outlined text-[48px] text-outline mb-2">event_busy</span>
            <p class="text-on-surface-variant">当日无考勤记录</p>
            <p class="text-xs text-outline mt-1">可能为休息日或尚未签到</p>
          </div>
        </div>

        <!-- Monthly View -->
        <div v-if="periodType === 'month' && reviewData" class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-6 shadow-sm">
          <h3 class="font-title-lg text-on-surface font-semibold mb-4">
            {{ selectedYear }}年{{ selectedMonth }}月 考勤汇总
          </h3>
          <!-- Stats Grid -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <div class="bg-emerald-50 rounded-lg p-3 text-center">
              <p class="text-xs text-emerald-700 mb-0.5">正常出勤</p>
              <p class="text-2xl font-bold text-emerald-800">{{ reviewData.normal_count ?? 0 }}</p>
            </div>
            <div class="bg-amber-50 rounded-lg p-3 text-center">
              <p class="text-xs text-amber-700 mb-0.5">迟到次数</p>
              <p class="text-2xl font-bold text-amber-800">{{ reviewData.late_count ?? 0 }}</p>
            </div>
            <div class="bg-amber-50 rounded-lg p-3 text-center">
              <p class="text-xs text-amber-700 mb-0.5">早退次数</p>
              <p class="text-2xl font-bold text-amber-800">{{ reviewData.early_leave_count ?? 0 }}</p>
            </div>
            <div class="bg-red-50 rounded-lg p-3 text-center">
              <p class="text-xs text-red-700 mb-0.5">缺勤天数</p>
              <p class="text-2xl font-bold text-red-800">{{ reviewData.absent_count ?? 0 }}</p>
            </div>
            <div class="bg-red-50 rounded-lg p-3 text-center">
              <p class="text-xs text-red-700 mb-0.5">无薪事假</p>
              <p class="text-2xl font-bold text-red-800">{{ reviewData.unpaid_leave_count ?? 0 }}</p>
            </div>
            <div class="bg-blue-50 rounded-lg p-3 text-center">
              <p class="text-xs text-blue-700 mb-0.5">年假(已批准)</p>
              <p class="text-2xl font-bold text-blue-800">{{ reviewData.approved_annual_leave_count ?? 0 }}</p>
            </div>
            <div class="bg-surface-container-low rounded-lg p-3 text-center">
              <p class="text-xs text-on-surface-variant mb-0.5">迟到总分钟</p>
              <p class="text-2xl font-bold text-on-surface">{{ reviewData.total_late_minutes ?? 0 }}</p>
            </div>
            <div class="bg-surface-container-low rounded-lg p-3 text-center">
              <p class="text-xs text-on-surface-variant mb-0.5">早退总分钟</p>
              <p class="text-2xl font-bold text-on-surface">{{ reviewData.total_early_leave_minutes ?? 0 }}</p>
            </div>
          </div>
          <!-- Annual Leave Balance -->
          <div class="border-t border-outline-variant/30 pt-4">
            <h4 class="text-sm font-semibold text-on-surface mb-2">年假余额</h4>
            <div class="flex gap-4 text-sm">
              <span>总额：<strong>{{ reviewData.total_days ?? 0 }}</strong> 天</span>
              <span>已用：<strong>{{ reviewData.used_days ?? 0 }}</strong> 天</span>
              <span>剩余：<strong class="text-primary">{{ reviewData.remaining_days ?? 0 }}</strong> 天</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right sidebar: Context -->
      <div class="lg:col-span-4">
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 shadow-sm p-6 flex flex-col justify-between h-full min-h-[300px]">
          <div>
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary shadow-sm">
                <span class="material-symbols-outlined">fact_check</span>
              </div>
              <div>
                <h3 class="font-title-lg text-title-lg text-on-surface font-semibold">考勤审查</h3>
                <span class="text-xs text-secondary bg-secondary-container/20 px-2 py-0.5 rounded-full">权限分层查询</span>
              </div>
            </div>
            <p class="text-sm text-on-surface-variant leading-relaxed">
              当前以 <strong>{{ currentRoleLabel }}</strong> 的授权范围查询
              <strong>{{ reviewData?.employee_name || '—' }}</strong> 的考勤记录。<br/><br/>
              部门主管仅可查看本部门员工考勤，HR 专员可查看全员考勤。
              所有查询操作均受权限系统约束。
            </p>
          </div>
          <div class="mt-6 border-t border-outline-variant/30 pt-4 text-center">
            <span class="text-[11px] text-outline font-label-md flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-[14px]">shield</span>
              考勤数据安全查询网关
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useAuthStore } from '../features/auth/authStore';
import { fetchAttendanceReview, type AttendanceReviewResponse } from '../shared/api/modules/attendance';
import { fetchEmployees } from '../shared/api/modules/employee';
import type { Employee } from '../shared/api/types';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import ErrorState from '../shared/components/feedback/ErrorState.vue';
import { ApiClientError } from '../shared/api/apiClient';

const { currentUser, hasAnyPermission } = useAuthStore();

const targetEmployeeId = ref<number>(currentUser.value?.employee_id || 0);
const employees = ref<Employee[]>([]);
const periodType = ref<'date' | 'month'>('date');
const reviewDate = ref(new Date().toISOString().slice(0, 10));
const selectedYear = ref(new Date().getFullYear());
const selectedMonth = ref(new Date().getMonth() + 1);

const reviewData = ref<AttendanceReviewResponse | null>(null);
const loading = ref(false);
const initialLoading = ref(true);
const accessError = ref<string | null>(null);
const serviceError = ref('');

const periodTypes = [
  { value: 'date' as const, label: '指定日期' },
  { value: 'month' as const, label: '指定月份' },
];

const currentRoleLabel = computed(() => ({
  EMPLOYEE: '普通员工',
  DEPARTMENT_MANAGER: '部门主管',
  HR_SPECIALIST: 'HR 专员',
  PAYROLL_ADMIN: '薪酬管理员',
}[currentUser.value?.role || 'EMPLOYEE'] ?? '普通员工'));

const canSelectTarget = computed(() => hasAnyPermission(['employee.department.read', 'payroll.all.read', 'audit.read']));

const filteredEmployees = computed(() => {
  if (hasAnyPermission(['payroll.all.read', 'audit.read'])) {
    return employees.value; // HR / Payroll admin: all
  }
  // Department manager: same department only
  if (hasAnyPermission(['employee.department.read'])) {
    const dept = currentUser.value?.department;
    return employees.value.filter(e => e.department === dept);
  }
  return employees.value;
});

function formatTime(val: string | null): string {
  if (!val) return '—';
  const d = new Date(val);
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const ss = String(d.getSeconds()).padStart(2, '0');
  return `${hh}:${mm}:${ss}`;
}

function statusColor(status: string): string {
  const map: Record<string, string> = {
    NORMAL: 'text-emerald-600',
    LATE: 'text-amber-600',
    EARLY_LEAVE: 'text-amber-600',
    ABSENT: 'text-red-600',
    UNPAID_LEAVE: 'text-red-600',
    APPROVED_ANNUAL_LEAVE: 'text-blue-600',
  };
  return map[status] || 'text-on-surface';
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    NORMAL: '正常',
    LATE: '迟到',
    EARLY_LEAVE: '早退',
    ABSENT: '缺勤',
    UNPAID_LEAVE: '无薪事假',
    APPROVED_ANNUAL_LEAVE: '年假(已批准)',
  };
  return map[status] || status;
}

async function fetchReview() {
  if (loading.value) return;
  loading.value = true;
  accessError.value = null;
  serviceError.value = '';
  try {
    const params: any = {
      target_employee_id: targetEmployeeId.value,
      period_type: periodType.value,
    };
    if (periodType.value === 'date') params.review_date = reviewDate.value;
    if (periodType.value === 'month') {
      params.year = selectedYear.value;
      params.month = selectedMonth.value;
    }
    reviewData.value = await fetchAttendanceReview(params);
  } catch (err: any) {
    reviewData.value = null;
    const message = err.message || '无法获取考勤数据';
    if (err instanceof ApiClientError && err.status === 403) accessError.value = message;
    else serviceError.value = message;
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  try {
    if (!currentUser.value?.employee_id) {
      serviceError.value = '当前账号未关联员工档案，无法查询考勤。';
      return;
    }
    targetEmployeeId.value = currentUser.value.employee_id;
    if (canSelectTarget.value) {
      try { employees.value = await fetchEmployees(); } catch { employees.value = []; }
    }
    await fetchReview();
  } finally {
    initialLoading.value = false;
  }
});
</script>
