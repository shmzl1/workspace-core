<template>
  <div class="p-4 md:p-8 pb-32 max-w-container-max mx-auto h-full flex flex-col overflow-y-auto">
    <!-- Header -->
    <div class="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h2 class="font-headline-lg md:font-display text-headline-lg-mobile md:text-display text-on-surface tracking-tight">薪资明细</h2>
        <p class="font-body-lg text-body-lg text-on-surface-variant mt-1">
          按当前授权范围查看员工薪资信息与字段可见状态。
        </p>
      </div>
      <button 
        @click="exportReport"
        class="bg-surface-container-lowest border border-outline-variant text-primary font-label-md text-label-md py-2 px-4 rounded-lg flex items-center gap-2 hover:bg-surface-container-low transition-colors shadow-sm"
      >
        <span class="material-symbols-outlined text-[18px]">download</span>
        导出 PDF
      </button>
    </div>

    <div class="bg-primary/5 rounded-xl border border-primary/20 p-5 mb-6">
      <h3 class="font-title-lg text-[16px] font-semibold text-primary mb-3 flex items-center gap-2">
        <span class="material-symbols-outlined text-[20px]">tune</span>
        薪资访问范围
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div>
          <span class="block text-xs font-medium text-on-surface-variant mb-1">当前访问角色</span>
          <p class="rounded-lg border border-outline-variant bg-white px-3 py-2.5 text-sm font-semibold text-on-surface">
            {{ currentRoleLabel }}
          </p>
        </div>
        <div v-if="canSelectTarget">
          <label class="block text-xs font-medium text-on-surface-variant mb-1">查询目标员工 ID</label>
          <select v-model.number="targetEmployeeId" class="w-full bg-white border border-outline-variant rounded-lg p-2.5 text-sm outline-none focus:border-primary">
            <option v-for="employee in employees" :key="employee.id" :value="employee.id">{{ employee.full_name }} · {{ employee.department }}</option>
          </select>
        </div>
        <div>
          <button 
            @click="fetchSalaryDetails"
            :disabled="salaryLoading"
            class="w-full bg-primary text-on-primary font-semibold py-2.5 px-4 rounded-lg text-sm hover:bg-primary-container transition-all flex items-center justify-center gap-1"
          >
            <span class="material-symbols-outlined text-sm">search</span>
            {{ salaryLoading ? '查询中……' : '查询薪资' }}
          </button>
        </div>
        <div class="text-xs text-outline leading-tight py-1">
          查询结果由薪资权限规则和审计记录共同约束。
        </div>
      </div>
    </div>

    <LoadingState v-if="initialLoading" message="正在读取薪资信息..." detail="正在执行薪资权限校验并写入审计记录" />

    <!-- Access Denied State -->
    <div v-else-if="accessError" class="bg-error-container/20 border border-error/30 rounded-xl p-8 text-center flex flex-col items-center justify-center mb-8">
      <div class="w-16 h-16 rounded-full bg-error/10 flex items-center justify-center text-error mb-4">
        <span class="material-symbols-outlined text-[36px]">gpp_bad</span>
      </div>
      <h3 class="font-headline-sm text-on-surface font-semibold mb-2">访问被拒绝 (Access Denied)</h3>
      <p class="text-sm text-on-surface-variant max-w-md leading-relaxed">
        系统鉴权服务拒绝了本次访问请求：{{ accessError }}。此尝试已被实时记录至权限审计日志中。
      </p>
    </div>

    <ErrorState
      v-else-if="serviceError"
      title="薪资数据暂时无法获取"
      :message="serviceError"
      retry-label="重新加载"
      @retry="fetchSalaryDetails"
    />

    <!-- Main Grid Layout (If Allowed) -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
      <!-- Left Column: Data & Table -->
      <div class="lg:col-span-8 flex flex-col gap-6">
        
        <!-- Hero Card: Net Pay & Month Selector -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-6 shadow-sm relative overflow-hidden">
          <div class="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4"></div>
          <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div>
              <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider mb-2">
                {{ selectedYear }}年{{ selectedMonth }}月 预计实发薪资 ({{ salaryCurrency || 'CNY' }})
              </p>
              <div class="font-display text-[42px] leading-[50px] font-bold text-on-surface tracking-tight mb-2">
                {{ salaryAmount !== null ? '¥ ' + Number(estimatedDeductions.netSalary).toLocaleString([], { minimumFractionDigits: 2 }) : '已隐藏 / 无权限' }}
              </div>
              <div class="flex items-center gap-2 text-secondary">
                <span class="material-symbols-outlined text-[16px]">verified_user</span>
                <span class="font-label-md text-label-md">已结合 {{ selectedMonth }} 月考勤月度统计进行预计算</span>
              </div>
            </div>
            <!-- Year/Month selectors -->
            <div class="flex items-center gap-2 bg-surface-container-low p-2 rounded-xl border border-outline-variant/30">
              <select v-model="selectedYear" @change="loadMonthlyAttendance" class="bg-white border border-outline-variant rounded-lg px-2.5 py-1 text-xs outline-none focus:border-primary">
                <option v-for="y in [2025, 2026, 2027]" :key="y" :value="y">{{ y }}年</option>
              </select>
              <select v-model="selectedMonth" @change="loadMonthlyAttendance" class="bg-white border border-outline-variant rounded-lg px-2.5 py-1 text-xs outline-none focus:border-primary">
                <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Breakdown Table -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 shadow-sm overflow-hidden">
          <div class="px-6 py-4 border-b border-outline-variant/30 bg-surface-container-low/50 flex justify-between items-center">
            <h3 class="font-title-lg text-title-lg text-on-surface font-semibold">薪资构成与有效期</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-surface-container-low/50 border-b border-outline-variant/30">
                  <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium w-1/3">项目</th>
                  <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium">数值/内容</th>
                  <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium text-right">权限状态</th>
                </tr>
              </thead>
              <tbody class="font-body-md text-body-md text-on-surface divide-y divide-outline-variant/20">
                <!-- Base Salary -->
                <tr class="hover:bg-surface-container-lowest transition-colors">
                  <td class="py-3.5 px-6 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-secondary"></div>
                    基本月薪 (Base Salary)
                  </td>
                  <td class="py-3.5 px-6 font-mono font-medium">
                    {{ salaryAmount !== null ? '¥ ' + salaryAmount : '**** (无权限)' }}
                  </td>
                  <td class="py-3.5 px-6 text-right">
                    <span :class="['px-2.5 py-0.5 rounded text-[11px] font-semibold', salaryAmount !== null ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700']">
                      {{ salaryAmount !== null ? '已授权' : '已脱敏' }}
                    </span>
                  </td>
                </tr>
                <!-- Currency -->
                <tr class="hover:bg-surface-container-lowest transition-colors">
                  <td class="py-3.5 px-6 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-secondary"></div>
                    结算币种 (Currency)
                  </td>
                  <td class="py-3.5 px-6 font-medium">
                    {{ salaryCurrency || '**** (无权限)' }}
                  </td>
                  <td class="py-3.5 px-6 text-right">
                    <span :class="['px-2.5 py-0.5 rounded text-[11px] font-semibold', salaryCurrency ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700']">
                      {{ salaryCurrency ? '已授权' : '已脱敏' }}
                    </span>
                  </td>
                </tr>
                <!-- Effective From -->
                <tr class="hover:bg-surface-container-lowest transition-colors">
                  <td class="py-3.5 px-6 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-secondary"></div>
                    生效起始日 (Effective From)
                  </td>
                  <td class="py-3.5 px-6 font-mono">
                    {{ effectiveFrom || '**** (无权限)' }}
                  </td>
                  <td class="py-3.5 px-6 text-right">
                    <span :class="['px-2.5 py-0.5 rounded text-[11px] font-semibold', effectiveFrom ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700']">
                      {{ effectiveFrom ? '已授权' : '已脱敏' }}
                    </span>
                  </td>
                </tr>
                <!-- Effective To -->
                <tr class="hover:bg-surface-container-lowest transition-colors">
                  <td class="py-3.5 px-6 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-secondary"></div>
                    生效截止日 (Effective To)
                  </td>
                  <td class="py-3.5 px-6 font-mono">
                    {{ effectiveTo || '**** (已脱敏/永久生效)' }}
                  </td>
                  <td class="py-3.5 px-6 text-right">
                    <span :class="['px-2.5 py-0.5 rounded text-[11px] font-semibold', effectiveTo ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700']">
                      {{ effectiveTo ? '已授权' : '已脱敏' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Attendance Deductions Table -->
        <div v-if="salaryAmount !== null" class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 shadow-sm overflow-hidden mt-2">
          <div class="px-6 py-4 border-b border-outline-variant/30 bg-surface-container-low/50 flex justify-between items-center">
            <h3 class="font-title-lg text-title-lg text-on-surface font-semibold flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[20px] text-amber-500">warning</span>
              考勤关联扣款明细 ({{ selectedYear }}年{{ selectedMonth }}月)
            </h3>
            <span class="text-xs text-outline leading-tight">数据隔离：考勤汇总直接作为预审输入</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-surface-container-low/50 border-b border-outline-variant/30">
                  <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium w-1/3">扣款项目</th>
                  <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium">考勤汇总</th>
                  <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium">扣款规则与计算</th>
                  <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium text-right">金额 (RMB)</th>
                </tr>
              </thead>
              <tbody class="font-body-md text-body-md text-on-surface divide-y divide-outline-variant/20">
                <!-- Base Salary Earning -->
                <tr class="hover:bg-surface-container-lowest transition-colors">
                  <td class="py-3.5 px-6 font-semibold flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
                    协议基本月薪
                  </td>
                  <td class="py-3.5 px-6 text-on-surface-variant">-</td>
                  <td class="py-3.5 px-6 text-on-surface-variant">协议标准工资额度</td>
                  <td class="py-3.5 px-6 text-right font-mono font-bold text-primary">
                    + ¥ {{ Number(salaryAmount).toLocaleString([], { minimumFractionDigits: 2 }) }}
                  </td>
                </tr>
                <!-- Late -->
                <tr class="hover:bg-surface-container-lowest transition-colors">
                  <td class="py-3.5 px-6 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-amber-500"></div>
                    迟到扣款
                  </td>
                  <td class="py-3.5 px-6 text-on-surface-variant">
                    {{ estimatedDeductions.lateCount }} 次
                  </td>
                  <td class="py-3.5 px-6 text-on-surface-variant">
                    50 元 / 次
                  </td>
                  <td class="py-3.5 px-6 text-right font-mono" :class="estimatedDeductions.lateDeduct > 0 ? 'text-error font-semibold' : 'text-outline'">
                    - ¥ {{ estimatedDeductions.lateDeduct.toFixed(2) }}
                  </td>
                </tr>
                <!-- Early Leave -->
                <tr class="hover:bg-surface-container-lowest transition-colors">
                  <td class="py-3.5 px-6 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-amber-500"></div>
                    早退扣款
                  </td>
                  <td class="py-3.5 px-6 text-on-surface-variant">
                    {{ estimatedDeductions.earlyCount }} 次
                  </td>
                  <td class="py-3.5 px-6 text-on-surface-variant">
                    50 元 / 次
                  </td>
                  <td class="py-3.5 px-6 text-right font-mono" :class="estimatedDeductions.earlyDeduct > 0 ? 'text-error font-semibold' : 'text-outline'">
                    - ¥ {{ estimatedDeductions.earlyDeduct.toFixed(2) }}
                  </td>
                </tr>
                <!-- Absent -->
                <tr class="hover:bg-surface-container-lowest transition-colors">
                  <td class="py-3.5 px-6 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-red-500"></div>
                    缺勤扣款
                  </td>
                  <td class="py-3.5 px-6 text-on-surface-variant">
                    {{ estimatedDeductions.absentCount }} 天
                  </td>
                  <td class="py-3.5 px-6 text-on-surface-variant">
                    天数 * 日薪 (日薪 = 基本月薪 / 22)
                  </td>
                  <td class="py-3.5 px-6 text-right font-mono" :class="estimatedDeductions.absentDeduct > 0 ? 'text-error font-semibold' : 'text-outline'">
                    - ¥ {{ estimatedDeductions.absentDeduct.toFixed(2) }}
                  </td>
                </tr>
                <!-- Unpaid Leave -->
                <tr class="hover:bg-surface-container-lowest transition-colors">
                  <td class="py-3.5 px-6 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-red-500"></div>
                    无薪事假扣款
                  </td>
                  <td class="py-3.5 px-6 text-on-surface-variant">
                    {{ estimatedDeductions.unpaidCount }} 天
                  </td>
                  <td class="py-3.5 px-6 text-on-surface-variant">
                    天数 * 日薪
                  </td>
                  <td class="py-3.5 px-6 text-right font-mono" :class="estimatedDeductions.unpaidDeduct > 0 ? 'text-error font-semibold' : 'text-outline'">
                    - ¥ {{ estimatedDeductions.unpaidDeduct.toFixed(2) }}
                  </td>
                </tr>
                <!-- Total deductions -->
                <tr class="bg-surface-container-low/50 font-semibold">
                  <td class="py-3 px-6" colspan="3">合计扣减金额</td>
                  <td class="py-3 px-6 text-right font-mono font-bold text-error">
                    - ¥ {{ estimatedDeductions.total.toLocaleString([], { minimumFractionDigits: 2 }) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Column: AI Assistant Contextual -->
      <div class="lg:col-span-4">
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 shadow-sm p-6 flex flex-col justify-between h-full min-h-[300px]">
          <div>
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary shadow-sm">
                <span class="material-symbols-outlined">smart_toy</span>
              </div>
              <div>
                <h3 class="font-title-lg text-title-lg text-on-surface font-semibold">薪资助手</h3>
                <span class="text-xs text-secondary bg-secondary-container/20 px-2 py-0.5 rounded-full">企业问答加密中</span>
              </div>
            </div>
            <p class="text-sm text-on-surface-variant leading-relaxed">
              当前以 <strong>{{ currentRoleLabel }}</strong> 的授权范围查询员工 ID 为 <strong>{{ targetEmployeeId }}</strong> 的薪资明细。<br/><br/>
              由于权限分层，HR、部门经理和薪酬管理员获得的结果互不相同。所有本次查阅（包括被拦截的请求）都已通过 API 管道实时写入系统审计底册。
            </p>
          </div>
          <div class="mt-6 border-t border-outline-variant/30 pt-4 text-center">
            <span class="text-[11px] text-outline font-label-md flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-[14px]">shield</span>
              基于三层架构的数据安全网关
            </span>
          </div>
        </div>
      </div>
    </div>

    <section v-if="canReviewPayroll" class="rounded-xl border border-outline-variant/50 bg-surface-container-lowest p-6 shadow-sm">
      <div class="mb-4 flex items-center justify-between gap-4"><div><h3 class="font-title-lg font-semibold text-on-surface">薪资预审</h3><p class="mt-1 text-sm text-on-surface-variant">查看待复核记录并由具备权限的人员生成预审建议。</p></div><button class="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white" @click="runPreAudit">生成预审建议</button></div>
      <p v-if="reviewNotice" class="mb-3 text-sm text-on-surface-variant">{{ reviewNotice }}</p>
      <div v-if="payrollReviews.length" class="grid gap-2"><div v-for="record in payrollReviews" :key="record.id" class="flex items-center justify-between rounded-lg bg-surface-container-low px-4 py-3 text-sm"><span>{{ record.employee_name || `员工 #${record.employee_id}` }} · {{ record.period_code || '当前周期' }}</span><span>{{ record.status }}</span></div></div>
      <p v-else class="text-sm text-on-surface-variant">暂无薪资预审记录。</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useAuthStore } from '../features/auth/authStore';
import { fetchEmployeeSalary, fetchMySalary } from '../shared/api/modules/payroll';
import { fetchMonthlyAttendanceSummary } from '../shared/api/modules/attendance';
import { fetchPayrollReviewRecords, reviewPayrollPreAudit, type PayrollReviewSummary } from '../shared/api/modules/payrollReview';
import { fetchEmployees } from '../shared/api/modules/employee';
import type { Employee } from '../shared/api/types';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import ErrorState from '../shared/components/feedback/ErrorState.vue';
import { ApiClientError } from '../shared/api/apiClient';

const emit = defineEmits(['show-toast']);
const { currentUser, hasAnyPermission, hasPermission } = useAuthStore();
const targetEmployeeId = ref<number>(currentUser.value?.employee_id || 0);
const employees = ref<Employee[]>([]);
const payrollReviews = ref<PayrollReviewSummary[]>([]);
const reviewNotice = ref('');

const salaryAmount = ref<number | null>(null);
const salaryCurrency = ref<string | null>(null);
const effectiveFrom = ref<string | null>(null);
const effectiveTo = ref<string | null>(null);
const accessError = ref<string | null>(null);
const serviceError = ref('');
const salaryLoading = ref(false);
const initialLoading = ref(true);

// --- Attendance-linked Payroll States ---
const selectedYear = ref(new Date().getFullYear());
const selectedMonth = ref(new Date().getMonth() + 1);
const monthlyAttendance = ref<any>(null);
const attendanceLoading = ref(false);

const currentRoleLabel = computed(() => ({
  EMPLOYEE: '普通员工',
  DEPARTMENT_MANAGER: '部门主管',
  HR_SPECIALIST: 'HR 专员',
  PAYROLL_ADMIN: '薪酬管理员',
}[currentUser.value?.role || 'EMPLOYEE'] ?? '普通员工'));
const canSelectTarget = computed(() => hasAnyPermission(['payroll.department.read', 'payroll.masked.read', 'payroll.all.read']));
const canReviewPayroll = computed(() => hasAnyPermission(['payroll.review.read', 'payroll.review.manage']));

const loadMonthlyAttendance = async () => {
  if (!targetEmployeeId.value) return;
  attendanceLoading.value = true;
  try {
    const data = await fetchMonthlyAttendanceSummary(
      selectedYear.value,
      selectedMonth.value,
      targetEmployeeId.value
    );
    monthlyAttendance.value = data;
  } catch (err) {
    console.error('Failed to load monthly attendance for payroll:', err);
    monthlyAttendance.value = null;
  } finally {
    attendanceLoading.value = false;
  }
};

const estimatedDeductions = computed(() => {
  if (!monthlyAttendance.value || salaryAmount.value === null) {
    return {
      lateCount: 0,
      earlyCount: 0,
      absentCount: 0,
      unpaidCount: 0,
      lateDeduct: 0,
      earlyDeduct: 0,
      absentDeduct: 0,
      unpaidDeduct: 0,
      total: 0,
      netSalary: salaryAmount.value || 0
    };
  }

  const baseSalary = salaryAmount.value;
  const standardDays = 22; // default standard work days per month
  const dailyRate = baseSalary / standardDays;

  const lateCount = monthlyAttendance.value.late_count || 0;
  const earlyCount = monthlyAttendance.value.early_leave_count || 0;
  const absentCount = monthlyAttendance.value.absent_count || 0;
  const unpaidCount = monthlyAttendance.value.unpaid_leave_count || 0;

  const lateDeduct = lateCount * 50;
  const earlyDeduct = earlyCount * 50;
  const absentDeduct = Math.round(absentCount * dailyRate * 100) / 100;
  const unpaidDeduct = Math.round(unpaidCount * dailyRate * 100) / 100;

  const total = lateDeduct + earlyDeduct + absentDeduct + unpaidDeduct;
  const netSalary = Math.max(0, baseSalary - total);

  return {
    lateCount,
    earlyCount,
    absentCount,
    unpaidCount,
    lateDeduct,
    earlyDeduct,
    absentDeduct,
    unpaidDeduct,
    total,
    netSalary
  };
});

const fetchSalaryDetails = async () => {
  if (salaryLoading.value) return;
  salaryLoading.value = true;
  accessError.value = null;
  serviceError.value = '';
  
  try {
    const data = currentUser.value?.employee_id === targetEmployeeId.value && hasPermission('payroll.self.read')
      ? await fetchMySalary()
      : await fetchEmployeeSalary(targetEmployeeId.value);
    salaryAmount.value = data.base_salary;
    salaryCurrency.value = data.currency;
    effectiveFrom.value = data.effective_from;
    effectiveTo.value = data.effective_to;
    await loadMonthlyAttendance();
  } catch (err: any) {
    salaryAmount.value = null;
    salaryCurrency.value = null;
    effectiveFrom.value = null;
    effectiveTo.value = null;
    const message = err.message || '无法获取薪资信息';
    if (err instanceof ApiClientError && err.status === 403) accessError.value = message;
    else serviceError.value = message;
  } finally {
    salaryLoading.value = false;
  }
};

const exportReport = () => {
  emit('show-toast', '薪资导出功能尚未配置。');
};

async function loadPayrollReviews() {
  if (!hasPermission('payroll.review.read')) return;
  try { payrollReviews.value = (await fetchPayrollReviewRecords()).records; } catch { payrollReviews.value = []; }
}

async function runPreAudit() {
  if (!hasPermission('payroll.review.manage')) return;
  try {
    const result = await reviewPayrollPreAudit({ requester_role: '', include_line_items: true });
    reviewNotice.value = result.message || '薪资预审建议已生成。';
    await loadPayrollReviews();
    await fetchSalaryDetails();
  } catch (error) {
    reviewNotice.value = error instanceof Error ? error.message : '薪资预审暂时无法执行。';
  }
}

onMounted(async () => {
  try {
    if (!currentUser.value?.employee_id) {
      serviceError.value = '当前账号未关联员工档案，无法查询薪资。';
      return;
    }
    targetEmployeeId.value = currentUser.value.employee_id;
    if (canSelectTarget.value) {
      try { employees.value = await fetchEmployees(); } catch { employees.value = []; }
    }
    await loadPayrollReviews();
    await fetchSalaryDetails();
  } finally {
    initialLoading.value = false;
  }
});
</script>
