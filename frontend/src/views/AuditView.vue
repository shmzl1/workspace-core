<template>
  <div class="pb-32 h-full overflow-y-auto pr-2">
    <!-- Page Header -->
    <div class="mb-8">
      <h2 class="font-display text-[28px] font-bold text-on-background mb-2">权限审计 (Permission Audit)</h2>
      <p class="font-body-lg text-body-lg text-on-surface-variant">监控、审计系统数据访问安全并提供 AI 权限合规风险预警。</p>
    </div>

    <!-- Stats & AI Alert Bento Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
      <!-- Radial Safety Gauge -->
      <div class="lg:col-span-4 bg-white rounded-xl border border-outline-variant/30 shadow-sm p-6 flex flex-col items-center justify-center min-h-[220px]">
        <h4 class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-4 text-center">系统安全合规评分</h4>
        <div class="relative w-32 h-32 flex items-center justify-center mb-2">
          <!-- Circular Progress Background -->
          <svg class="absolute w-full h-full transform -rotate-90">
            <circle cx="64" cy="64" r="54" stroke="var(--color-line)" stroke-width="8" fill="transparent" />
            <circle cx="64" cy="64" r="54" stroke="var(--color-primary)" stroke-dasharray="339.3" stroke-dashoffset="20.3" stroke-width="8" fill="transparent" stroke-linecap="round" class="transition-all duration-1000" />
          </svg>
          <div class="text-center">
            <span class="font-display text-4xl font-extrabold text-on-surface leading-none">{{合规评分}}</span>
            <span class="text-xs text-outline block mt-0.5">/ 100</span>
          </div>
        </div>
        <span class="text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded font-semibold mt-1 flex items-center gap-1">
          <span class="material-symbols-outlined text-[12px]">check_circle</span> 安全评级：极高
        </span>
      </div>

      <!-- AI Audit Suggestion Box -->
      <div class="lg:col-span-8 bg-white rounded-xl border border-outline-variant/30 shadow-sm p-6 relative overflow-hidden group">
        <div class="absolute right-0 top-0 w-32 h-32 bg-primary-container/5 rounded-bl-full -z-10 group-hover:scale-110 transition-transform duration-500"></div>
        <div class="flex items-start gap-4 h-full flex-col justify-between">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center shrink-0 text-primary">
              <span class="material-symbols-outlined text-[28px]">auto_awesome</span>
            </div>
            <div>
              <h3 class="font-title-lg text-title-lg text-on-background mb-1 flex items-center gap-2">
                AI 权限风险分析
                <span v-if="deniedLogsCount > 0" class="bg-amber-100 text-amber-800 text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider animate-pulse">检测到越权预警</span>
                <span v-else class="bg-emerald-100 text-emerald-800 text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider">无越权警告</span>
              </h3>
              <p class="font-body-md text-body-md text-on-surface-variant leading-relaxed mt-1">
                <span v-if="deniedLogsCount > 0">
                  发现普通员工角色尝试越权读取他人 `薪资明细` 接口的拦截记录。此类违规请求已被系统拦截。请检查是否为调试接口时的不合规操作。
                </span>
                <span v-else>
                  近 24 小时内未发现异常权限越权行为，所有薪资明细及核心接口调用均通过 `salary_access_control` 权限网关合法进行。系统合规状态优良。
                </span>
              </p>
            </div>
          </div>
          <div class="flex gap-3 mt-4">
            <button class="px-4 py-2 bg-primary text-on-primary rounded-lg font-medium hover:bg-primary/95 text-xs transition-all shadow-sm">
              一键安全加固
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Metrics Row -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-xl border border-outline-variant/30 p-5 shadow-sm">
        <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-1">合规控制项</p>
        <h3 class="font-display text-[28px] font-bold text-on-surface">4 <span class="text-xs text-outline font-normal">个分层权限角色</span></h3>
      </div>
      <div class="bg-white rounded-xl border border-outline-variant/30 p-5 shadow-sm">
        <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-1">敏感资源审计事件</p>
        <h3 class="font-display text-[28px] font-bold text-on-surface">{{ totalLogsCount }} <span class="text-xs text-outline font-normal">条审计记录</span></h3>
      </div>
      <div class="bg-white rounded-xl border border-outline-variant/30 p-5 shadow-sm">
        <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-1">越权拦截事件</p>
        <h3 class="font-display text-[28px] font-bold text-error">{{ deniedLogsCount }} <span class="text-xs text-error/80 font-normal ml-2">次拦截</span></h3>
      </div>
    </div>

    <!-- Audit Log List -->
    <div class="bg-white rounded-xl border border-outline-variant/30 shadow-sm p-6">
      <div class="flex justify-between items-center mb-6">
        <h3 class="font-headline-md text-headline-md text-on-background font-semibold">敏感权限操作日志</h3>
        <div class="flex gap-2">
          <button 
            @click="fetchAuditLogs"
            class="px-3 py-1.5 bg-surface-container-low border border-outline-variant text-primary rounded-lg font-medium text-xs hover:bg-surface-container transition-colors flex items-center gap-1"
          >
            <span class="material-symbols-outlined text-[14px]">refresh</span> 刷新日志
          </button>
        </div>
      </div>

      <div class="overflow-x-auto w-full">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-outline-variant/30 text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
              <th class="pb-3 pl-2">操作用户</th>
              <th class="pb-3">部门与角色</th>
              <th class="pb-3">动作 & 资源</th>
              <th class="pb-3">请求字段</th>
              <th class="pb-3">时间</th>
              <th class="pb-3">操作 IP</th>
              <th class="pb-3 text-right pr-2">审计状态</th>
            </tr>
          </thead>
          <tbody class="text-xs divide-y divide-outline-variant/20 text-on-surface">
            <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-surface-container-lowest transition-colors">
              <td class="py-3.5 pl-2 font-medium flex items-center gap-2">
                <span class="w-7 h-7 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-[11px]">
                  {{ getActorName(log.actor_user_id)[0] }}
                </span>
                {{ getActorName(log.actor_user_id) }}
              </td>
              <td class="py-3.5 text-on-surface-variant">
                {{ getRoleDisplay(log.actor_role) }}
              </td>
              <td class="py-3.5">
                <span class="px-2 py-0.5 bg-blue-50 text-blue-700 rounded font-mono text-[10px]">
                  {{ log.action }} [{{ log.resource_type }} #{{ log.resource_id || '' }}]
                </span>
              </td>
              <td class="py-3.5 text-outline max-w-[150px] truncate">
                {{ log.requested_fields.join(', ') }}
              </td>
              <td class="py-3.5 text-outline">
                {{ formatTimestamp(log.created_at) }}
              </td>
              <td class="py-3.5 font-mono text-outline">
                {{ log.ip_address || '127.0.0.1' }}
              </td>
              <td class="py-3.5 text-right pr-2">
                <span :class="['inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-semibold', 
                             log.result === 'ALLOWED' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700']">
                  <span :class="['w-1.5 h-1.5 rounded-full', log.result === 'ALLOWED' ? 'bg-emerald-500' : 'bg-rose-500']"></span>
                  {{ log.result === 'ALLOWED' ? '已授权' : '被拦截 (AI)' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Mock caller details to access audit logs
const mockHeaders = {
  'X-Mock-User-Id': '4', // Wang Qiang (PAYROLL_ADMIN)
  'X-Mock-Role': 'PAYROLL_ADMIN',
  'Content-Type': 'application/json'
};

interface AuditLog {
  id: number;
  actor_user_id: number | null;
  actor_role: str;
  target_employee_id: number | null;
  action: str;
  resource_type: str;
  resource_id: number | null;
  requested_fields: string[];
  result: str;
  reason: str | None;
  ip_address: str | None;
  user_agent: str | None;
  created_at: string;
}

const auditLogs = ref<AuditLog[]>([]);

const totalLogsCount = computed(() => auditLogs.value.length);
const deniedLogsCount = computed(() => auditLogs.value.filter(l => l.result === 'DENIED').length);
const 合规评分 = computed(() => {
  // Deduct 2 points for each denied attempt (max 10 points)
  const deduction = Math.min(deniedLogsCount.value * 2, 10);
  return 98 - deduction;
});

const getActorName = (userId: number | null): string => {
  if (userId === 1) return '张伟';
  if (userId === 2) return '李明';
  if (userId === 3) return '林雨晴';
  if (userId === 4) return '王强';
  return `用户 #${userId || '未知'}`;
};

const getRoleDisplay = (role: string): string => {
  if (role === 'EMPLOYEE') return '研发部 • 员工';
  if (role === 'DEPARTMENT_MANAGER') return '研发部 • 部门主管';
  if (role === 'HR_SPECIALIST') return '招聘部 • HR专员';
  if (role === 'PAYROLL_ADMIN') return '财务部 • 薪酬管理员';
  return role;
};

const formatTimestamp = (isoString: string) => {
  const d = new Date(isoString);
  return d.toLocaleString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

const fetchAuditLogs = async () => {
  try {
    const res = await fetch(`${apiBase}/audit/logs?limit=100`, { headers: mockHeaders });
    const json = await res.json();
    if (json.success && json.data) {
      auditLogs.value = json.data;
    }
  } catch (err) {
    console.error('Failed to fetch audit logs:', err);
  }
};

onMounted(() => {
  fetchAuditLogs();
});
</script>
