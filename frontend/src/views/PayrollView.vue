<template>
  <div class="payroll-page">
    <!-- 加载态 -->
    <LoadingState
      v-if="loading"
      message="正在获取薪资数据…"
      detail="连接薪资服务中"
    />

    <!-- 权限拒绝 -->
    <PermissionDenied
      v-else-if="permissionDenied"
      description="你当前的角色无权查看薪资明细，如需协助请联系 HR 管理员。"
    />

    <!-- 错误态 -->
    <ErrorState
      v-else-if="error"
      :message="error"
      retry-label="重新加载"
      @retry="retry"
    />

    <!-- 空态 -->
    <EmptyState
      v-else-if="isEmpty"
      title="暂无薪资记录"
      description="当前月份没有找到薪资数据，请联系 HR 确认。"
    />

    <!-- 正常内容 -->
    <template v-else>
      <div class="payroll-page__inner">
        <!-- 左列 -->
        <div class="payroll-page__main">
          <!-- Header -->
          <div class="payroll-page__header">
            <div>
              <h2>薪资明细</h2>
              <p>{{ currentYear }}年 {{ currentMonth }}月 | {{ employee.department }} - {{ employee.job_title }}</p>
            </div>
            <button class="payroll-page__export-btn" @click="emit('show-toast', '薪资 PDF 已生成。')">
              <span class="material-symbols-outlined" style="font-size:18px">download</span>
              导出 PDF
            </button>
          </div>

          <!-- Hero：实发薪资 -->
          <div class="payroll-page__hero">
            <div class="payroll-page__hero-bg"></div>
            <div class="payroll-page__hero-content">
              <div>
                <p class="payroll-page__hero-label">本月实发工资 (CNY)</p>
                <div class="payroll-page__hero-amount">
                  ¥ {{ payrollDetail.net_salary.toLocaleString() }}
                </div>
                <div class="payroll-page__hero-trend">
                  <span class="material-symbols-outlined" style="font-size:14px">trending_up</span>
                  <span>较上月增长 {{ trendPercent }}%</span>
                </div>
              </div>
              <div class="payroll-page__hero-badges">
                <div class="payroll-page__hero-badge">
                  <p>应发总额</p>
                  <strong>{{ payrollDetail.gross_salary.toLocaleString() }}</strong>
                </div>
                <div class="payroll-page__hero-badge">
                  <p>代扣代缴</p>
                  <strong>{{ totalDeductions.toLocaleString() }}</strong>
                </div>
              </div>
            </div>
          </div>

          <!-- 薪资构成明细表 -->
          <div class="payroll-page__table-card">
            <div class="payroll-page__table-header">
              <h3>薪资构成明细</h3>
              <button class="payroll-page__info-btn" @click="emit('show-toast', '薪资构成说明已展示。')">
                <span class="material-symbols-outlined">info</span>
              </button>
            </div>
            <div class="payroll-page__table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>项目</th>
                    <th>金额 (¥)</th>
                    <th>说明</th>
                  </tr>
                </thead>
                <tbody>
                  <!-- 收入项 -->
                  <tr v-for="item in incomeItems" :key="item.name">
                    <td>
                      <span class="dot dot--green"></span>
                      {{ item.name }}
                    </td>
                    <td>{{ item.amount.toLocaleString() }}</td>
                    <td>{{ item.note }}</td>
                  </tr>
                  <!-- 扣款项 -->
                  <tr v-for="item in deductionItems" :key="item.name" class="tr--deduction">
                    <td>
                      <span class="dot dot--red"></span>
                      {{ item.name }}
                    </td>
                    <td>-{{ item.amount.toLocaleString() }}</td>
                    <td>{{ item.note }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td>实发合计</td>
                    <td class="td--primary" colspan="2">{{ payrollDetail.net_salary.toLocaleString() }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- 年度趋势 -->
          <div class="payroll-page__chart-card">
            <div class="payroll-page__chart-header">
              <h3>年度收入趋势</h3>
              <select class="payroll-page__year-select">
                <option>{{ currentYear }}</option>
              </select>
            </div>
            <div class="payroll-page__chart">
              <div
                v-for="(h, idx) in trendHeights"
                :key="idx"
                class="payroll-page__chart-bar"
                :class="{ 'payroll-page__chart-bar--current': idx === currentMonth - 1 }"
                :style="{ height: `${h}%` }"
              ></div>
            </div>
            <div class="payroll-page__chart-labels">
              <span v-for="m in months" :key="m">{{ m }}</span>
            </div>
          </div>
        </div>

        <!-- 右列：薪资助手 -->
        <div class="payroll-page__assistant">
          <div class="payroll-page__assistant-card">
            <div class="payroll-page__assistant-header">
              <div class="payroll-page__assistant-avatar">
                <span class="material-symbols-outlined">smart_toy</span>
              </div>
              <div>
                <h3>薪资助理</h3>
                <p class="payroll-page__assistant-status">
                  <span class="dot dot--green"></span>
                  在线支持中
                </p>
              </div>
            </div>

            <div class="payroll-page__assistant-chat">
              <div class="payroll-page__assistant-msg">
                <div class="payroll-page__assistant-msg-avatar">
                  <span class="material-symbols-outlined" style="font-size:14px">smart_toy</span>
                </div>
                <div class="payroll-page__assistant-msg-bubble">
                  {{ assistantMessage }}
                </div>
              </div>
              <div class="payroll-page__assistant-suggestions">
                <button
                  v-for="q in quickQuestions"
                  :key="q"
                  class="payroll-page__assistant-chip"
                  @click="emit('show-toast', `薪资助理正在查询：${q}`)"
                >
                  {{ q }}
                </button>
              </div>
            </div>

            <div class="payroll-page__assistant-input">
              <div class="payroll-page__assistant-input-wrap">
                <input
                  type="text"
                  placeholder="向智能助手提问关于薪资的细节..."
                />
                <button>
                  <span class="material-symbols-outlined" style="font-size:16px">arrow_upward</span>
                </button>
              </div>
              <p class="payroll-page__assistant-disclaimer">
                <span class="material-symbols-outlined" style="font-size:11px">lock</span>
                您的对话经企业级加密，安全合规
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import ErrorState from '../shared/components/feedback/ErrorState.vue';
import EmptyState from '../shared/components/feedback/EmptyState.vue';
import PermissionDenied from '../shared/components/feedback/PermissionDenied.vue';
import { mockPayrollDetail, mockEmployee } from '../mock/payroll';

const emit = defineEmits<{
  'show-toast': [message: string];
}>();

// ── 状态 ─────────────────────────────────────
const loading = ref(true);
const error = ref<string | null>(null);
const permissionDenied = ref(false);
const isEmpty = ref(false);

const employee = ref(mockEmployee);
const payrollDetail = ref(mockPayrollDetail);
const currentYear = ref(2026);
const currentMonth = ref(7);

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const trendHeights = [60, 65, 62, 68, 65, 70, 75, 72, 78, 85, 10, 10];

const assistantMessage = computed(() => {
  const bonus = payrollDetail.value.breakdown.performance_bonus;
  return `您好，我是您的专属薪资助理。${currentMonth.value}月份薪资已发放${payrollDetail.value.checkOutAt ? '' : '（预览）'}，您本月有 ${bonus.toLocaleString()} 元的绩效奖金入账，恭喜！\n\n关于本月薪资明细，您有任何疑问吗？`;
});

const quickQuestions = [
  '本月个税是怎么扣除的？',
  '查看专项附加扣除详情',
  '下载年度薪资证明',
];

const totalDeductions = computed(() => {
  return Object.values(payrollDetail.value.deductions).reduce((a, b) => a + b, 0);
});

const trendPercent = computed(() => {
  // 模拟环比
  return '2.4';
});

const incomeItems = computed(() => [
  { name: '基本工资', amount: payrollDetail.value.breakdown.base_salary, note: '--' },
  { name: '绩效奖金', amount: payrollDetail.value.breakdown.performance_bonus, note: 'A 级绩效' },
  { name: '各类津贴', amount: payrollDetail.value.breakdown.allowances, note: '交通餐饮补贴' },
]);

const deductionItems = computed(() => payrollDetail.value.deduction_details);

function retry() {
  loading.value = false;
  error.value = null;
  // 重新加载
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 600);
}

onMounted(() => {
  setTimeout(() => {
    loading.value = false;
  }, 500);
});
</script>

<style scoped lang="scss">
.payroll-page {
  padding-bottom: 32px;
}

.payroll-page__inner {
  max-width: 1440px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(320px, 0.7fr);
  gap: 20px;
}

// ── Header ───────────────────────────────────
.payroll-page__header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;

  h2 {
    margin: 0;
    font-size: 28px;
    font-weight: 800;
    color: var(--color-text);
  }

  p {
    margin: 6px 0 0;
    color: var(--color-muted);
    font-size: 14px;
  }
}

.payroll-page__export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

// ── Hero ─────────────────────────────────────
.payroll-page__hero {
  position: relative;
  padding: 28px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: #fff;
  box-shadow: var(--shadow-card);
  overflow: hidden;
  margin-bottom: 20px;
}

.payroll-page__hero-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(36,85,245,0.04), transparent 70%);
  transform: translate(30%, -40%);
  pointer-events: none;
}

.payroll-page__hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.payroll-page__hero-label {
  margin: 0;
  font-size: 12px;
  font-weight: 800;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.payroll-page__hero-amount {
  font-size: 44px;
  font-weight: 900;
  color: var(--color-text);
  margin: 6px 0;
  line-height: 1;
}

.payroll-page__hero-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
  color: #15803d;
}

.payroll-page__hero-badges {
  display: flex;
  gap: 14px;
}

.payroll-page__hero-badge {
  padding: 14px 18px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: var(--color-surface-soft);

  p {
    margin: 0;
    font-size: 12px;
    color: var(--color-muted);
  }

  strong {
    display: block;
    margin-top: 4px;
    font-size: 20px;
    color: var(--color-text);
  }
}

// ── 表格 ─────────────────────────────────────
.payroll-page__table-card {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: #fff;
  box-shadow: var(--shadow-card);
  overflow: hidden;
  margin-bottom: 20px;
}

.payroll-page__table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-line);

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
  }
}

.payroll-page__info-btn {
  padding: 4px;
  border: 0;
  border-radius: 4px;
  background: none;
  color: var(--color-primary);
  cursor: pointer;
}

.payroll-page__table-wrap {
  overflow-x: auto;

  table {
    width: 100%;
    border-collapse: collapse;

    th {
      padding: 10px 20px;
      background: rgba(0,0,0,0.01);
      font-size: 11px;
      font-weight: 800;
      color: var(--color-muted);
      text-transform: uppercase;
      text-align: left;
    }

    td {
      padding: 12px 20px;
      font-size: 14px;
      color: var(--color-text);
      border-bottom: 1px solid rgba(0,0,0,0.04);
    }

    tbody tr:hover {
      background: rgba(36,85,245,0.02);
    }

    .tr--deduction td {
      color: var(--color-muted);
      background: rgba(239,68,68,0.02);
    }

    tfoot td {
      font-weight: 800;
      background: rgba(0,0,0,0.02);
      border-bottom: 0;
    }

    .td--primary {
      color: var(--color-primary);
    }
  }
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;

  &--green { background: #16a34a; }
  &--red { background: #e55c3c; }
}

// ── 图表 ─────────────────────────────────────
.payroll-page__chart-card {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: #fff;
  box-shadow: var(--shadow-card);
  padding: 20px;
}

.payroll-page__chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  h3 { margin: 0; font-size: 16px; font-weight: 700; }
}

.payroll-page__year-select {
  padding: 4px 10px;
  border: 1px solid var(--color-line);
  border-radius: 6px;
  font-size: 13px;
  background: var(--color-surface-soft);
  cursor: pointer;
}

.payroll-page__chart {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 180px;
  padding: 8px 0;
}

.payroll-page__chart-bar {
  flex: 1;
  border-radius: 4px 4px 0 0;
  background: rgba(36,85,245,0.12);
  transition: 0.2s;

  &--current {
    background: var(--color-primary);
    box-shadow: 0 0 12px rgba(36,85,245,0.25);
  }
}

.payroll-page__chart-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;

  span {
    font-size: 10px;
    color: var(--color-subtle);
    text-align: center;
    flex: 1;
  }
}

// ── 助手 ─────────────────────────────────────
.payroll-page__assistant-card {
  position: sticky;
  top: 92px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: #fff;
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  overflow: hidden;
}

.payroll-page__assistant-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-line);

  h3 { margin: 0; font-size: 15px; }
  p { margin: 2px 0 0; font-size: 12px; color: var(--color-muted); }
}

.payroll-page__assistant-avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.payroll-page__assistant-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.payroll-page__assistant-chat {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payroll-page__assistant-msg {
  display: flex;
  gap: 10px;
}

.payroll-page__assistant-msg-avatar {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  flex-shrink: 0;
}

.payroll-page__assistant-msg-bubble {
  padding: 12px 14px;
  border: 1px solid rgba(36,85,245,0.15);
  border-radius: 14px;
  border-top-left-radius: 4px;
  background: var(--color-surface-soft);
  font-size: 13px;
  color: var(--color-text);
  line-height: 1.6;
  white-space: pre-line;
}

.payroll-page__assistant-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-left: 38px;
}

.payroll-page__assistant-chip {
  padding: 6px 14px;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: #fff;
  color: var(--color-muted);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.15s;

  &:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
  }
}

.payroll-page__assistant-input {
  padding: 12px 16px;
  border-top: 1px solid var(--color-line);
}

.payroll-page__assistant-input-wrap {
  display: flex;
  align-items: center;
  padding: 4px;
  border: 1px solid var(--color-line);
  border-radius: 14px;
  background: var(--color-surface-soft);
  transition: 0.2s;

  &:focus-within {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(36,85,245,0.08);
  }

  input {
    flex: 1;
    border: 0;
    background: transparent;
    font-size: 13px;
    padding: 6px 10px;
    outline: none;
  }

  button {
    display: grid;
    width: 30px;
    height: 30px;
    place-items: center;
    border: 0;
    border-radius: 50%;
    background: var(--color-primary);
    color: #fff;
    cursor: pointer;
    flex-shrink: 0;
  }
}

.payroll-page__assistant-disclaimer {
  margin: 8px 0 0;
  font-size: 10px;
  color: var(--color-subtle);
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

@media (max-width: 1120px) {
  .payroll-page__inner {
    grid-template-columns: 1fr;
  }
}
</style>
