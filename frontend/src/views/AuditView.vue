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
            <span class="font-display text-4xl font-extrabold text-on-surface leading-none">94</span>
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
                <span class="bg-amber-100 text-amber-800 text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider animate-pulse">1 项预警</span>
              </h3>
              <p class="font-body-md text-body-md text-on-surface-variant leading-relaxed mt-1">
                上周研发部员工（非HR账号）尝试读取 `薪资字典` API 的调用频次异常上升。AI 评估这可能是由于研发端联调接口时的权限配置漏洞导致。建议检查接口鉴权策略，及时回撤不合规调用凭据。
              </p>
            </div>
          </div>
          <div class="flex gap-3 mt-4">
            <button class="px-4 py-2 bg-primary text-on-primary rounded-lg font-medium hover:bg-primary/95 text-xs transition-all shadow-sm">
              一键加固接口
            </button>
            <button class="px-4 py-2 bg-surface-container-low text-on-surface-variant border border-outline-variant/50 rounded-lg hover:bg-surface-container font-medium text-xs transition-all">
              忽略此警告
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Metrics Row -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-xl border border-outline-variant/30 p-5 shadow-sm">
        <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-1">监控权限项</p>
        <h3 class="font-display text-[28px] font-bold text-on-surface">48 <span class="text-xs text-outline font-normal">个模块权限</span></h3>
      </div>
      <div class="bg-white rounded-xl border border-outline-variant/30 p-5 shadow-sm">
        <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-1">敏感资源访问 (24h)</p>
        <h3 class="font-display text-[28px] font-bold text-on-surface">1,245 <span class="text-xs text-emerald-600 font-semibold ml-2">+12%</span></h3>
      </div>
      <div class="bg-white rounded-xl border border-outline-variant/30 p-5 shadow-sm">
        <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-1">异常审计事件</p>
        <h3 class="font-display text-[28px] font-bold text-error">1 <span class="text-xs text-error/80 font-normal ml-2">待处理</span></h3>
      </div>
    </div>

    <!-- Audit Log List -->
    <div class="bg-white rounded-xl border border-outline-variant/30 shadow-sm p-6">
      <div class="flex justify-between items-center mb-6">
        <h3 class="font-headline-md text-headline-md text-on-background font-semibold">敏感权限操作日志</h3>
        <div class="flex gap-2">
          <input class="px-3 py-1.5 bg-surface-container-low border border-outline-variant rounded-lg text-xs outline-none focus:border-primary w-48" placeholder="搜索用户或操作..." type="text"/>
          <button class="px-3 py-1.5 bg-surface-container-low border border-outline-variant text-on-surface-variant rounded-lg font-medium text-xs hover:bg-surface-container-medium transition-colors flex items-center gap-1">
            <span class="material-symbols-outlined text-[14px]">filter_alt</span> 筛选
          </button>
        </div>
      </div>

      <div class="overflow-x-auto w-full">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-outline-variant/30 text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
              <th class="pb-3 pl-2">操作用户</th>
              <th class="pb-3">部门与角色</th>
              <th class="pb-3">请求资源</th>
              <th class="pb-3">动作</th>
              <th class="pb-3">时间</th>
              <th class="pb-3">网络 IP</th>
              <th class="pb-3 text-right pr-2">审计状态</th>
            </tr>
          </thead>
          <tbody class="text-xs divide-y divide-outline-variant/20 text-on-surface">
            <!-- Row 1 -->
            <tr class="hover:bg-surface-container-lowest transition-colors">
              <td class="py-3.5 pl-2 font-medium flex items-center gap-2">
                <span class="w-7 h-7 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-[11px]">林</span>
                林雨晴
              </td>
              <td class="py-3.5 text-on-surface-variant">招聘部 • HR专员</td>
              <td class="py-3.5 font-mono text-outline">/api/v1/salary/access_control</td>
              <td class="py-3.5"><span class="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full font-medium">读取</span></td>
              <td class="py-3.5 text-outline">3 分钟前</td>
              <td class="py-3.5 font-mono text-outline">192.168.1.102</td>
              <td class="py-3.5 text-right pr-2">
                <span class="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-semibold">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> 已授权
                </span>
              </td>
            </tr>
            <!-- Row 2 -->
            <tr class="hover:bg-surface-container-lowest transition-colors">
              <td class="py-3.5 pl-2 font-medium flex items-center gap-2">
                <span class="w-7 h-7 rounded-full bg-secondary/10 text-secondary flex items-center justify-center font-bold text-[11px]">张</span>
                张伟
              </td>
              <td class="py-3.5 text-on-surface-variant">研发部 • 高级工程师</td>
              <td class="py-3.5 font-mono text-outline">/api/v1/salary/access_control</td>
              <td class="py-3.5"><span class="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full font-medium">读取</span></td>
              <td class="py-3.5 text-outline">1 小时前</td>
              <td class="py-3.5 font-mono text-outline">10.0.4.15</td>
              <td class="py-3.5 text-right pr-2">
                <span class="inline-flex items-center gap-1 bg-rose-50 text-rose-700 px-2 py-0.5 rounded-full font-semibold">
                  <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span> 已拦截 (AI)
                </span>
              </td>
            </tr>
            <!-- Row 3 -->
            <tr class="hover:bg-surface-container-lowest transition-colors">
              <td class="py-3.5 pl-2 font-medium flex items-center gap-2">
                <span class="w-7 h-7 rounded-full bg-tertiary/10 text-tertiary flex items-center justify-center font-bold text-[11px]">李</span>
                李明
              </td>
              <td class="py-3.5 text-on-surface-variant">研发部 • 研发经理</td>
              <td class="py-3.5 font-mono text-outline">/api/v1/employees/export</td>
              <td class="py-3.5"><span class="px-2 py-0.5 bg-amber-50 text-amber-700 rounded-full font-medium">写入</span></td>
              <td class="py-3.5 text-outline">4 小时前</td>
              <td class="py-3.5 font-mono text-outline">10.0.4.12</td>
              <td class="py-3.5 text-right pr-2">
                <span class="inline-flex items-center gap-1 bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full font-semibold">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span> 待审核
                </span>
              </td>
            </tr>
            <!-- Row 4 -->
            <tr class="hover:bg-surface-container-lowest transition-colors">
              <td class="py-3.5 pl-2 font-medium flex items-center gap-2">
                <span class="w-7 h-7 rounded-full bg-outline-variant/20 text-on-surface-variant flex items-center justify-center font-bold text-[11px]">王</span>
                王强
              </td>
              <td class="py-3.5 text-on-surface-variant">运维部 • 系统管理员</td>
              <td class="py-3.5 font-mono text-outline">/api/v1/admin/roles/update</td>
              <td class="py-3.5"><span class="px-2 py-0.5 bg-purple-50 text-purple-700 rounded-full font-medium">写入</span></td>
              <td class="py-3.5 text-outline">1 天前</td>
              <td class="py-3.5 font-mono text-outline">192.168.1.1</td>
              <td class="py-3.5 text-right pr-2">
                <span class="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-semibold">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> 已授权
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
// Simple static presentation
</script>
