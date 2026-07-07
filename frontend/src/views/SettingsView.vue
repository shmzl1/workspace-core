<template>
  <div class="pb-32 h-full overflow-y-auto pr-2">
    <!-- Page Header -->
    <div class="mb-8">
      <h2 class="font-display text-[28px] font-bold text-on-background mb-2">系统设置 (System Settings)</h2>
      <p class="font-body-lg text-body-lg text-on-surface-variant">配置 TalentFlow AI 智聘中枢的底层大模型接口、招聘自动化模块及安全策略。</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Left Column: Settings Categories -->
      <div class="lg:col-span-8 space-y-6">
        <!-- AI Agent Configuration -->
        <div class="bg-white rounded-xl border border-outline-variant/30 shadow-sm p-6">
          <h3 class="font-title-lg text-title-lg font-semibold text-on-surface mb-6 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">smart_toy</span> AI 招聘 Agent 设置
          </h3>
          
          <div class="space-y-6">
            <!-- Parsing Toggle -->
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-semibold text-on-surface">启用 AI 简历智能解析</h4>
                <p class="text-xs text-on-surface-variant mt-0.5">自动从上传的 PDF/Word 简历中提取结构化人才字段并同步到候选人池。</p>
              </div>
              <button class="relative inline-flex h-6 w-11 items-center shrink-0 cursor-pointer rounded-full transition-colors duration-200 ease-in-out focus:outline-none bg-primary" type="button">
                <span class="pointer-events-none inline-block h-4 w-4 transform translate-x-6 rounded-full bg-white shadow transition duration-200 ease-in-out"></span>
              </button>
            </div>
            
            <div class="w-full h-px bg-outline-variant/20"></div>

            <!-- Scoring Toggle -->
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-semibold text-on-surface">启用 AI 简历评分初筛</h4>
                <p class="text-xs text-on-surface-variant mt-0.5">使用自定义岗位匹配度大模型对新候选人进行简历匹配度自动打分。</p>
              </div>
              <button class="relative inline-flex h-6 w-11 items-center shrink-0 cursor-pointer rounded-full transition-colors duration-200 ease-in-out focus:outline-none bg-primary" type="button">
                <span class="pointer-events-none inline-block h-4 w-4 transform translate-x-6 rounded-full bg-white shadow transition duration-200 ease-in-out"></span>
              </button>
            </div>

            <div class="w-full h-px bg-outline-variant/20"></div>

            <!-- Auto Scheduling Toggle -->
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-semibold text-on-surface">启用 AI 智能面试排班</h4>
                <p class="text-xs text-on-surface-variant mt-0.5">AI 助手根据面试官与候选人的空闲时间，自动推荐并预订最合适的日历档期。</p>
              </div>
              <button class="relative inline-flex h-6 w-11 items-center shrink-0 cursor-pointer rounded-full transition-colors duration-200 ease-in-out focus:outline-none bg-surface-container-high" type="button">
                <span class="pointer-events-none inline-block h-4 w-4 transform translate-x-1 rounded-full bg-white shadow transition duration-200 ease-in-out"></span>
              </button>
            </div>

            <div class="w-full h-px bg-outline-variant/20"></div>

            <!-- Strictness Slider -->
            <div>
              <div class="flex justify-between items-center mb-2">
                <h4 class="text-sm font-semibold text-on-surface">AI 初筛严格度偏好</h4>
                <span class="text-xs text-primary font-bold bg-primary/10 px-2 py-0.5 rounded">75% (严格推荐)</span>
              </div>
              <p class="text-xs text-on-surface-variant mb-3">严格度越高，进入“最佳匹配”推荐列表的简历评分门槛越高（当前阈值：80分）。</p>
              <input class="w-full h-1.5 bg-surface-container rounded-lg appearance-none cursor-pointer accent-primary" type="range" min="0" max="100" value="75"/>
            </div>
          </div>
        </div>

        <!-- Security Settings -->
        <div class="bg-white rounded-xl border border-outline-variant/30 shadow-sm p-6">
          <h3 class="font-title-lg text-title-lg font-semibold text-on-surface mb-6 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">security</span> 安全机制与敏感权限策略
          </h3>
          <div class="space-y-6">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-semibold text-on-surface">启用 AI 动态权限审计与异常拦截</h4>
                <p class="text-xs text-on-surface-variant mt-0.5">当检测到外部 IP 异常高频调用考勤、薪资相关接口时，AI 自动阻断其访问。</p>
              </div>
              <button class="relative inline-flex h-6 w-11 items-center shrink-0 cursor-pointer rounded-full transition-colors duration-200 ease-in-out focus:outline-none bg-primary" type="button">
                <span class="pointer-events-none inline-block h-4 w-4 transform translate-x-6 rounded-full bg-white shadow transition duration-200 ease-in-out"></span>
              </button>
            </div>

            <div class="w-full h-px bg-outline-variant/20"></div>

            <div>
              <h4 class="text-sm font-semibold text-on-surface mb-2">敏感数据脱敏范围</h4>
              <p class="text-xs text-on-surface-variant mb-4">勾选后，没有特定薪资预审权限的账号在预览员工列表和数据报表时，以下敏感信息将被自动脱敏（星号处理）。</p>
              <div class="flex flex-wrap gap-4">
                <label class="flex items-center gap-2 text-xs text-on-surface font-medium cursor-pointer">
                  <input class="rounded border-outline-variant text-primary focus:ring-primary w-4 h-4 cursor-pointer" type="checkbox" checked/>
                  薪资期望与明细 (Salary Info)
                </label>
                <label class="flex items-center gap-2 text-xs text-on-surface font-medium cursor-pointer">
                  <input class="rounded border-outline-variant text-primary focus:ring-primary w-4 h-4 cursor-pointer" type="checkbox" checked/>
                  身份证及护照号 (ID Numbers)
                </label>
                <label class="flex items-center gap-2 text-xs text-on-surface font-medium cursor-pointer">
                  <input class="rounded border-outline-variant text-primary focus:ring-primary w-4 h-4 cursor-pointer" type="checkbox"/>
                  考勤异常惩罚记录 (Disciplinary Logs)
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Status & Save -->
      <div class="lg:col-span-4 space-y-6">
        <!-- Integration Status -->
        <div class="bg-white rounded-xl border border-outline-variant/30 shadow-sm p-6">
          <h3 class="font-title-lg text-title-lg font-semibold text-on-surface mb-4">系统集成状态</h3>
          <div class="space-y-4">
            <!-- LLM -->
            <div class="flex items-center justify-between p-3 rounded-lg bg-surface-container-low border border-outline-variant/20">
              <div class="flex items-center gap-2.5">
                <span class="material-symbols-outlined text-primary text-[20px]">hub</span>
                <div>
                  <h4 class="text-xs font-semibold text-on-surface">大语言模型接口</h4>
                  <p class="text-[10px] text-outline font-mono">GPT-4o via API</p>
                </div>
              </div>
              <span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] rounded font-bold">健康</span>
            </div>
            <!-- ChromaDB -->
            <div class="flex items-center justify-between p-3 rounded-lg bg-surface-container-low border border-outline-variant/20">
              <div class="flex items-center gap-2.5">
                <span class="material-symbols-outlined text-primary text-[20px]">database</span>
                <div>
                  <h4 class="text-xs font-semibold text-on-surface">向量数据库</h4>
                  <p class="text-[10px] text-outline font-mono">ChromaDB Local</p>
                </div>
              </div>
              <span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] rounded font-bold">已连接</span>
            </div>
            <!-- PostgreSQL -->
            <div class="flex items-center justify-between p-3 rounded-lg bg-surface-container-low border border-outline-variant/20">
              <div class="flex items-center gap-2.5">
                <span class="material-symbols-outlined text-primary text-[20px]">storage</span>
                <div>
                  <h4 class="text-xs font-semibold text-on-surface">主关系数据库</h4>
                  <p class="text-[10px] text-outline font-mono">PostgreSQL 16</p>
                </div>
              </div>
              <span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] rounded font-bold">已连接</span>
            </div>
          </div>
        </div>

        <!-- Slack & Webhook -->
        <div class="bg-white rounded-xl border border-outline-variant/30 shadow-sm p-6">
          <h3 class="font-title-lg text-title-lg font-semibold text-on-surface mb-3">企业应用推送 Webhook</h3>
          <p class="text-xs text-on-surface-variant mb-4">当 AI 触发权限审计拦截或者新候选人进入面试时，自动向该 Webhook 接口推送通知。</p>
          <div class="space-y-3">
            <div>
              <label class="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider block mb-1">Webhook URL</label>
              <input class="w-full px-3 py-2 bg-surface-container-low border border-outline-variant rounded-lg text-xs outline-none focus:border-primary font-mono text-on-surface" type="text" value="https://hooks.slack.com/services/T000/B000/XXXXXX"/>
            </div>
            <button class="w-full py-2 bg-surface-container text-on-surface border border-outline-variant/60 rounded-lg text-xs font-semibold hover:bg-surface-container-high transition-colors">
              测试发送模拟通知
            </button>
          </div>
        </div>

        <!-- Save Button Card -->
        <div class="bg-surface-container-lowest p-1">
          <button class="w-full py-3 bg-primary text-on-primary rounded-xl font-body-md font-semibold hover:shadow-lg hover:bg-primary/95 transition-all flex items-center justify-center gap-2 text-sm shadow-md">
            <span class="material-symbols-outlined text-[20px]">save</span>
            保存所有设置 (Save Settings)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Simple static presentation
</script>
