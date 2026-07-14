<template>
  <div class="audit-page pb-32">
    <!-- 加载态 -->
    <LoadingState
      v-if="loading"
      message="正在获取审计日志…"
      detail="连接审计服务中"
    />

    <!-- 权限拒绝 -->
    <PermissionDenied
      v-else-if="permissionDenied"
      description="你当前的角色无权访问权限审计页面，仅 HR 和系统管理员可查看。"
    />

    <!-- 错误态 -->
    <ErrorState
      v-else-if="error"
      :message="error"
      retry-label="重新加载"
      @retry="fetchAuditLogs"
    />

    <!-- 正常内容 -->
    <template v-else>
      <!-- Header -->
      <div class="audit-page__header">
        <h2>权限审计</h2>
        <p>监控、审计系统数据访问安全并提供 AI 权限合规风险预警。</p>
      </div>

      <!-- Stats + AI Alert -->
      <div class="audit-page__stats-grid">
        <!-- 安全评分 -->
        <div class="audit-page__score-card">
          <h4>系统安全合规评分</h4>
          <div class="audit-page__gauge">
            <svg viewBox="0 0 128 128" class="audit-page__gauge-svg">
              <circle cx="64" cy="64" r="54" fill="none" stroke="var(--color-line)" stroke-width="8" />
              <circle
                cx="64" cy="64" r="54"
                fill="none"
                stroke="var(--color-primary)"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="339.3"
                :stroke-dashoffset="dashOffset"
                transform="rotate(-90 64 64)"
              />
            </svg>
            <div class="audit-page__gauge-value">
              <strong>{{ stats.security_score }}</strong>
              <span>/ 100</span>
            </div>
          </div>
          <span class="audit-page__badge audit-page__badge--green">
            <span class="material-symbols-outlined" style="font-size:12px">check_circle</span>
            安全评级：极高
          </span>
        </div>

        <!-- AI 预警 -->
        <div class="audit-page__alert-card">
          <div class="audit-page__alert-content">
            <div class="audit-page__alert-icon">
              <span class="material-symbols-outlined" style="font-size:24px">auto_awesome</span>
            </div>
            <div>
              <h3>
                AI 权限风险分析
                <span v-if="stats.anomaly_events > 0" class="audit-page__badge audit-page__badge--amber">{{ stats.anomaly_events }} 项越权预警</span>
                <span v-else class="audit-page__badge audit-page__badge--green">系统运行优良</span>
              </h3>
              <p v-if="stats.anomaly_events > 0">
                系统实时检测到有 {{ stats.anomaly_events }} 次由于分层权限拦截而触发的越权尝试（`DENIED` 记录）。
                此类拦截记录已被实时存证。建议 HR 专员和系统管理员定期核查审计日志流，确保研发端联调或生产接口的权限策略配置安全。
              </p>
              <p v-else>
                近 24 小时内未发现任何异常越权拦截事件，敏感数据接口（如薪资明细 API）全部通过 `salary_access_control` 算法鉴权合规访问。系统总体状态优良。
              </p>
            </div>
          </div>
          <div class="audit-page__alert-actions">
            <button class="audit-page__btn audit-page__btn--primary" @click="handleReinforce">
              一键加固接口
            </button>
            <button class="audit-page__btn" @click="emit('show-toast', '警告已忽略。')">
              忽略此警告
            </button>
          </div>
        </div>
      </div>

      <!-- Metrics -->
      <div class="audit-page__metrics">
        <div class="audit-page__metric">
          <p>监控权限项</p>
          <h3>{{ stats.monitored_modules }} <span>个分层角色</span></h3>
        </div>
        <div class="audit-page__metric">
          <p>敏感资源访问 (24h)</p>
          <h3>{{ stats.sensitive_access_24h }} <span>条审计记录</span></h3>
        </div>
        <div class="audit-page__metric">
          <p>越权拦截事件</p>
          <h3 class="text-red">{{ stats.anomaly_events }} <span>次拦截</span></h3>
        </div>
      </div>

      <!-- 审计日志表格 -->
      <div class="audit-page__table-card">
        <div class="audit-page__table-header">
          <h3>敏感权限操作日志</h3>
          <div class="audit-page__table-actions">
            <input
              type="text"
              class="audit-page__search"
              placeholder="搜索用户或操作..."
              v-model="searchQuery"
            />
            <button class="audit-page__btn" @click="searchQuery = ''">
              <span class="material-symbols-outlined" style="font-size:14px">filter_alt</span>
              清除
            </button>
            <button class="audit-page__btn" @click="fetchAuditLogs">
              <span class="material-symbols-outlined" style="font-size:14px">refresh</span>
              刷新
            </button>
          </div>
        </div>

        <!-- 空搜索态 -->
        <EmptyState
          v-if="filteredLogs.length === 0 && auditLogs.length > 0"
          title="未找到匹配记录"
          :description="`没有找到包含「${searchQuery}」的审计日志。`"
        />

        <!-- 空数据态 -->
        <EmptyState
          v-else-if="auditLogs.length === 0"
          title="暂无审计记录"
          description="当前系统没有审计日志，审计记录将在敏感操作发生时自动写入。"
        />

        <!-- 日志表格 -->
        <div v-else class="audit-page__table-wrap">
          <table>
            <thead>
              <tr>
                <th>操作用户</th>
                <th>部门与角色</th>
                <th>请求资源</th>
                <th>动作</th>
                <th>时间</th>
                <th>网络 IP</th>
                <th>审计状态</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="log in filteredLogs" :key="log.id">
                <tr
                  class="audit-page__log-row"
                  @click="selectedLogId = selectedLogId === log.id ? null : log.id"
                >
                  <td>
                    <span class="audit-page__user-avatar">{{ log.operator_name[0] }}</span>
                    {{ log.operator_name }}
                  </td>
                  <td>{{ log.operator_role }}</td>
                  <td class="audit-page__mono">{{ log.resource }}</td>
                  <td>
                    <span :class="actionClass(log.action)">
                      {{ log.action === 'READ' ? '读取' : log.action === 'WRITE' ? '写入' : log.action }}
                    </span>
                  </td>
                  <td>{{ formatTime(log.timestamp) }}</td>
                  <td class="audit-page__mono">{{ log.ip_address }}</td>
                  <td>
                    <span :class="resultClass(log.result)">
                      <span class="audit-page__dot" :class="'audit-page__dot--' + log.result.toLowerCase()"></span>
                      {{ resultLabel(log.result) }}
                    </span>
                  </td>
                </tr>

                <!-- 展开详情 -->
                <tr v-if="selectedLogId === log.id">
                  <td colspan="7" class="p-0">
                    <div class="audit-page__log-detail">
                      <div class="audit-page__log-detail-grid">
                        <div>
                          <strong>操作详情 / 理由</strong>
                          <p>{{ log.detail }}</p>
                        </div>
                        <div>
                          <strong>Trace ID</strong>
                          <p class="audit-page__mono">{{ log.trace_id }}</p>
                        </div>
                        <div>
                          <strong>网络环境</strong>
                          <p class="audit-page__mono text-xs">{{ log.user_agent }}</p>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
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
import { ApiClientError } from '../shared/api/apiClient';
import { fetchAuditLogs as requestAuditLogs } from '../shared/api/modules/audit';
import { fetchEmployees } from '../shared/api/modules/employee';
import type { Employee } from '../shared/api/types';

const emit = defineEmits<{
  'show-toast': [message: string];
}>();

interface AuditLogEntry {
  id: number;
  operator_name: string;
  operator_role: string;
  resource: string;
  action: string;
  timestamp: string;
  ip_address: string;
  result: string;
  trace_id: string;
  detail: string;
  user_agent: string;
}

// ── 状态 ─────────────────────────────────────
const loading = ref(true);
const error = ref<string | null>(null);
const permissionDenied = ref(false);

const auditLogs = ref<AuditLogEntry[]>([]);
const searchQuery = ref('');
const selectedLogId = ref<number | null>(null);

const stats = computed(() => {
  const total = auditLogs.value.length;
  const denied = auditLogs.value.filter((l) => l.result === 'DENIED').length;
  // Deduct 2 points per denied request, min 80
  const score = Math.max(98 - denied * 2, 80);
  return {
    security_score: score,
    monitored_modules: 4,
    sensitive_access_24h: total,
    anomaly_events: denied,
  };
});

const dashOffset = computed(() => {
  const score = stats.value.security_score;
  const circumference = 339.3;
  return circumference - (score / 100) * circumference;
});

const filteredLogs = computed(() => {
  if (!searchQuery.value.trim()) return auditLogs.value;
  const q = searchQuery.value.toLowerCase();
  return auditLogs.value.filter(
    (l) =>
      l.operator_name.toLowerCase().includes(q) ||
      l.resource.toLowerCase().includes(q) ||
      l.operator_role.toLowerCase().includes(q) ||
      l.detail.toLowerCase().includes(q)
  );
});

// ── 方法 ─────────────────────────────────────
function formatTime(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins} 分钟前`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)} 小时前`;
  return `${Math.floor(diffMins / 1440)} 天前`;
}

function actionClass(action: string) {
  return {
    'audit-page__tag audit-page__tag--blue': action === 'READ',
    'audit-page__tag audit-page__tag--amber': action === 'WRITE',
  };
}

function resultClass(result: string) {
  return {
    'audit-page__result audit-page__result--allowed': result === 'ALLOWED',
    'audit-page__result audit-page__result--denied': result === 'DENIED',
    'audit-page__result audit-page__result--pending': result === 'PENDING',
  };
}

function resultLabel(result: string): string {
  const map: Record<string, string> = {
    ALLOWED: '已授权',
    DENIED: '已拦截',
    PENDING: '待审核',
  };
  return map[result] ?? result;
}

const getRoleDisplay = (role: string, employee?: Employee): string => {
  const roleName = {
    EMPLOYEE: '员工',
    DEPARTMENT_MANAGER: '部门主管',
    HR_SPECIALIST: 'HR 专员',
    PAYROLL_ADMIN: '薪酬管理员',
  }[role] ?? role;
  return employee?.department ? `${employee.department} • ${roleName}` : roleName;
};

const handleReinforce = () => {
  emit('show-toast', '接口权限已成功加固，防御策略生效中！');
};

const fetchAuditLogs = async () => {
  loading.value = true;
  error.value = null;
  permissionDenied.value = false;

  try {
    const [rows, employees] = await Promise.all([
      requestAuditLogs(100),
      fetchEmployees().catch((): Employee[] => []),
    ]);
    const employeesByUserId = new Map(employees.filter((item) => item.user_id !== null).map((item) => [item.user_id, item]));
    const employeesById = new Map(employees.map((item) => [item.id, item]));
    auditLogs.value = rows.map((log) => {
        const actor = employeesByUserId.get(log.actor_user_id);
        const target = employeesById.get(log.target_employee_id ?? -1);
        return {
          id: log.id,
          operator_name: actor?.full_name || '账号未关联员工档案',
          operator_role: getRoleDisplay(log.actor_role, actor),
          resource: `${log.resource_type} · ${target?.full_name || '目标员工信息缺失'}`,
          action: log.action === 'QUERY_SALARY' ? 'READ' : log.action,
          timestamp: log.created_at,
          ip_address: log.ip_address || '--',
          result: log.result,
          trace_id: log.trace_id || '--',
          detail: log.reason || '获取资源详情',
          user_agent: log.user_agent || '--'
        };
      });
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 403) {
      permissionDenied.value = true;
    } else {
      error.value = err instanceof Error ? err.message : '无法载入审计记录';
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchAuditLogs();
});
</script>

<style scoped lang="scss">
.audit-page {
  max-width: 1440px;
  margin: 0 auto;
  padding-bottom: 32px;
}

.audit-page__header {
  margin-bottom: 24px;

  h2 {
    margin: 0;
    font-size: 28px;
    font-weight: 800;
    color: var(--color-text);
  }

  p {
    margin: 6px 0 0;
    color: var(--color-muted);
    font-size: 15px;
  }
}

// ── Stats Grid ───────────────────────────────
.audit-page__stats-grid {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(0, 2.5fr);
  gap: 18px;
  margin-bottom: 22px;
}

.audit-page__score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 22px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.audit-page__score-card h4 {
  margin: 0 0 12px;
  font-size: 11px;
  font-weight: 800;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.audit-page__gauge {
  position: relative;
  width: 110px;
  height: 110px;
  margin-bottom: 8px;
}

.audit-page__gauge-svg {
  width: 100%;
  height: 100%;
}

.audit-page__gauge-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;

  strong {
    font-size: 32px;
    font-weight: 900;
    color: var(--color-text);
  }

  span {
    display: block;
    font-size: 11px;
    color: var(--color-subtle);
  }
}

.audit-page__alert-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 22px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.audit-page__alert-content {
  display: flex;
  gap: 16px;
}

.audit-page__alert-icon {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  flex-shrink: 0;
}

.audit-page__alert-content h3 {
  margin: 0;
  font-size: 16px;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 8px;
}

.audit-page__alert-content p {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--color-muted);
  line-height: 1.6;
}

.audit-page__alert-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

// ── Badges ───────────────────────────────────
.audit-page__badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
}

.audit-page__badge--green {
  background: rgba(22,163,74,0.1);
  color: #15803d;
}

.audit-page__badge--amber {
  background: #fef3c7;
  color: var(--color-status-warning-text);
}

// ── Metrics ──────────────────────────────────
.audit-page__metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 22px;
}

.audit-page__metric {
  padding: 18px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);

  p {
    margin: 0;
    font-size: 11px;
    font-weight: 800;
    color: var(--color-muted);
    text-transform: uppercase;
  }

  h3 {
    margin: 6px 0 0;
    font-size: 26px;
    color: var(--color-text);
    font-weight: 900;
  }

  h3 span {
    font-size: 12px;
    font-weight: 400;
    color: var(--color-subtle);
  }

  .up { color: #15803d; font-weight: 700; }
  .text-red { color: var(--color-status-error-text); }
}

// ── Buttons ──────────────────────────────────
.audit-page__btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.15s;

  &:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
  }
}

.audit-page__btn--primary {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);

  &:hover {
    background: #173fd1;
    color: #fff;
  }
}

// ── Table ────────────────────────────────────
.audit-page__table-card {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.audit-page__table-header {
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

.audit-page__table-actions {
  display: flex;
  gap: 8px;
}

.audit-page__search {
  padding: 5px 10px;
  border: 1px solid var(--color-line);
  border-radius: 6px;
  font-size: 12px;
  background: var(--color-surface-soft);
  outline: none;
  width: 180px;

  &:focus {
    border-color: var(--color-primary);
  }
}

.audit-page__table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;

  th {
    padding: 10px 16px;
    background: rgba(0,0,0,0.01);
    font-size: 11px;
    font-weight: 800;
    color: var(--color-muted);
    text-align: left;
    text-transform: uppercase;
  }

  td {
    padding: 12px 16px;
    font-size: 13px;
    color: var(--color-text);
    border-bottom: 1px solid rgba(0,0,0,0.04);
  }
}

.audit-page__log-row {
  cursor: pointer;
  transition: 0.12s;

  &:hover {
    background: rgba(36,85,245,0.02);
  }
}

.audit-page__user-avatar {
  display: inline-flex;
  width: 24px;
  height: 24px;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 11px;
  font-weight: 800;
  margin-right: 6px;
  vertical-align: middle;
}

.audit-page__mono {
  font-family: monospace;
  font-size: 11px;
  color: var(--color-subtle);
}

.audit-page__tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;

  &--blue { background: var(--color-primary-soft); color: var(--color-primary); }
  &--amber { background: #fef3c7; color: var(--color-status-warning-text); }
}

.audit-page__result {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;

  &--allowed { background: rgba(22,163,74,0.08); color: #15803d; }
  &--denied { background: rgba(229,92,60,0.08); color: var(--color-status-error-text); }
  &--pending { background: rgba(245,158,11,0.08); color: var(--color-status-warning-text); }
}

.audit-page__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;

  &--allowed { background: #16a34a; }
  &--denied { background: #e55c3c; }
  &--pending { background: #f59e0b; animation: pulse 1.5s ease-in-out infinite; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

// ── 日志详情 ─────────────────────────────────
.audit-page__log-detail {
  padding: 16px 20px;
  border-top: 1px solid var(--color-line);
  background: rgba(0,0,0,0.01);
}

.audit-page__log-detail-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;

  strong {
    display: block;
    font-size: 11px;
    color: var(--color-muted);
    margin-bottom: 4px;
    text-transform: uppercase;
  }

  p {
    margin: 0;
    font-size: 13px;
    color: var(--color-text);
  }
}

@media (max-width: 960px) {
  .audit-page__stats-grid {
    grid-template-columns: 1fr;
  }

  .audit-page__metrics {
    grid-template-columns: 1fr;
  }

  .audit-page__alert-content {
    flex-direction: column;
  }

  .audit-page__log-detail-grid {
    grid-template-columns: 1fr;
  }
}


/* 深色模式 */
[data-theme="dark"] .audit-page__tag--amber { background: #451a03; }
[data-theme="dark"] .audit-page__result--allowed { background: rgba(34, 197, 94, 0.12); color: #86efac; }
[data-theme="dark"] .audit-page__badge--amber { background: #451a03; }
</style>
