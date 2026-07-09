<template>
  <div class="p-4 md:p-8 pb-32 max-w-container-max mx-auto h-full flex flex-col overflow-y-auto">
    <!-- Header -->
    <div class="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h2 class="font-headline-lg md:font-display text-headline-lg-mobile md:text-display text-on-surface tracking-tight">薪资明细</h2>
        <p class="font-body-lg text-body-lg text-on-surface-variant mt-1">
          三 Sprint 开发计划：确定性业务核心闭环
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

    <!-- Mock Role Debug Dashboard (Visible to all for evaluation/demonstration) -->
    <div class="bg-primary/5 rounded-xl border border-primary/20 p-5 mb-6">
      <h3 class="font-title-lg text-[16px] font-semibold text-primary mb-3 flex items-center gap-2">
        <span class="material-symbols-outlined text-[20px]">tune</span>
        模拟权限与字段脱敏调试台
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label class="block text-xs font-medium text-on-surface-variant mb-1">选择访问者身份</label>
          <select 
            v-model="mockUser" 
            @change="handleMockUserChange"
            class="w-full bg-white border border-outline-variant rounded-lg p-2.5 text-sm outline-none focus:border-primary"
          >
            <option :value="1">普通员工 (张伟 - 研发部)</option>
            <option :value="2">部门经理 (李明 - 研发部)</option>
            <option :value="3">HR专员 (林雨晴 - 人资部)</option>
            <option :value="4">薪酬管理员 (王强 - 财务部)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-on-surface-variant mb-1">查询目标员工 ID</label>
          <input 
            type="number" 
            v-model.number="targetEmployeeId"
            class="w-full bg-white border border-outline-variant rounded-lg p-2.5 text-sm outline-none focus:border-primary"
            min="1" 
            max="10"
          />
        </div>
        <div>
          <button 
            @click="fetchSalaryDetails"
            class="w-full bg-primary text-on-primary font-semibold py-2.5 px-4 rounded-lg text-sm hover:bg-primary-container transition-all flex items-center justify-center gap-1"
          >
            <span class="material-symbols-outlined text-sm">search</span>
            执行鉴权查询
          </button>
        </div>
        <div class="text-xs text-outline leading-tight py-1">
          提示：不同角色对不同员工的薪资查询，将受到 <code class="bg-surface-container px-1 py-0.5 rounded text-[11px] font-mono">salary_access_control</code> 算法控制。
        </div>
      </div>
    </div>

    <!-- Access Denied State -->
    <div v-if="accessError" class="bg-error-container/20 border border-error/30 rounded-xl p-8 text-center flex flex-col items-center justify-center mb-8">
      <div class="w-16 h-16 rounded-full bg-error/10 flex items-center justify-center text-error mb-4">
        <span class="material-symbols-outlined text-[36px]">gpp_bad</span>
      </div>
      <h3 class="font-headline-sm text-on-surface font-semibold mb-2">访问被拒绝 (Access Denied)</h3>
      <p class="text-sm text-on-surface-variant max-w-md leading-relaxed">
        系统鉴权服务拒绝了本次访问请求：{{ accessError }}。此尝试已被实时记录至权限审计日志中。
      </p>
    </div>

    <!-- Main Grid Layout (If Allowed) -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
      <!-- Left Column: Data & Table -->
      <div class="lg:col-span-8 flex flex-col gap-6">
        
        <!-- Hero Card: Net Pay -->
        <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-6 shadow-sm relative overflow-hidden">
          <div class="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4"></div>
          <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div>
              <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider mb-2">基本应发薪资 ({{ salaryCurrency || 'CNY' }})</p>
              <div class="font-display text-[48px] leading-[56px] font-bold text-on-surface tracking-tight mb-2">
                {{ salaryAmount !== null ? '¥ ' + Number(salaryAmount).toLocaleString([], { minimumFractionDigits: 2 }) : '已隐藏 / 无权限' }}
              </div>
              <div class="flex items-center gap-2 text-secondary">
                <span class="material-symbols-outlined text-[16px]">verified_user</span>
                <span class="font-label-md text-label-md">已通过安全规则验证</span>
              </div>
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
              您当前以访问者 ID 为 <strong>{{ mockUser }}</strong> 的身份，查询目标员工 ID 为 <strong>{{ targetEmployeeId }}</strong> 的薪资明细。<br/><br/>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { setDevIdentity, type DevIdentity } from '../shared/api/apiClient';
import { fetchEmployeeSalary, fetchMySalary } from '../shared/api/modules/payroll';

const props = defineProps({
  role: {
    type: String,
    default: 'employee'
  }
});

const emit = defineEmits(['show-toast']);

const mockUser = ref(1); // Default to Zhang Wei (EMPLOYEE)
const targetEmployeeId = ref(1); // Default to querying Employee 1

const salaryAmount = ref<number | null>(null);
const salaryCurrency = ref<string | null>(null);
const effectiveFrom = ref<string | null>(null);
const effectiveTo = ref<string | null>(null);
const accessError = ref<string | null>(null);

const handleMockUserChange = () => {
  if (mockUser.value === 1) {
    targetEmployeeId.value = 1;
  }
  fetchSalaryDetails();
};

const applySelectedIdentity = () => {
  const roles: Record<number, DevIdentity['role']> = {
    1: 'EMPLOYEE',
    2: 'DEPARTMENT_MANAGER',
    3: 'HR_SPECIALIST',
    4: 'PAYROLL_ADMIN',
  };
  setDevIdentity({ userId: mockUser.value, role: roles[mockUser.value] || 'EMPLOYEE' });
};

const fetchSalaryDetails = async () => {
  accessError.value = null;
  
  try {
    applySelectedIdentity();
    const data = mockUser.value === targetEmployeeId.value
      ? await fetchMySalary()
      : await fetchEmployeeSalary(targetEmployeeId.value);
    salaryAmount.value = data.base_salary;
    salaryCurrency.value = data.currency;
    effectiveFrom.value = data.effective_from;
    effectiveTo.value = data.effective_to;
  } catch (err: any) {
    salaryAmount.value = null;
    salaryCurrency.value = null;
    effectiveFrom.value = null;
    effectiveTo.value = null;
    accessError.value = err.message || '无法获取薪资信息';
    console.error('Failed to fetch salary:', err);
  }
};

const exportReport = () => {
  emit('show-toast', 'PDF 薪资证明已生成演示预览并保存。');
};

// Monitor the parent shell's role change
watch(() => props.role, (newRole) => {
  if (newRole === 'employee') {
    mockUser.value = 1;
    targetEmployeeId.value = 1;
  } else {
    mockUser.value = 3;
    targetEmployeeId.value = 1;
  }
  fetchSalaryDetails();
});

onMounted(() => {
  if (props.role === 'employee') {
    mockUser.value = 1;
    targetEmployeeId.value = 1;
  } else {
    mockUser.value = 3;
    targetEmployeeId.value = 1;
  }
  fetchSalaryDetails();
});
</script>
