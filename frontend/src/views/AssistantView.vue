<template>
<div class="flex-1 flex flex-col h-[calc(100vh-64px)] relative overflow-hidden bg-surface">
      <!-- Background Decorative -->
      <div class="absolute top-[20%] -left-[10%] w-96 h-96 bg-primary/10 rounded-full blur-[100px] pointer-events-none" />
      <div class="absolute bottom-[-10%] right-[10%] w-80 h-80 bg-secondary-container/20 rounded-full blur-[80px] pointer-events-none" />

      <div class="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col xl:flex-row gap-8 max-w-[1600px] mx-auto w-full z-10">
        
        <!-- Main Chat Area -->
        <div class="flex-1 bg-surface-container-lowest/80 rounded-2xl border border-outline-variant/40 shadow-xl shadow-primary/5 flex flex-col overflow-hidden glass-card">
          
          <!-- Chat Header -->
          <div class="px-6 py-4 border-b border-outline-variant/40 bg-surface-container-lowest/50 backdrop-blur-md flex justify-between items-center relative overflow-hidden">
            <div class="flex items-center gap-4 relative z-10">
              <div class="relative w-12 h-12">
                <div class="absolute inset-0 bg-gradient-to-tr from-primary to-tertiary rounded-xl blur-[8px] opacity-60 animate-pulse" />
                <div class="relative w-12 h-12 rounded-xl bg-surface-container-lowest border border-primary/20 flex items-center justify-center text-primary shadow-sm z-10">
                  <span class="material-symbols-outlined text-[28px] bg-clip-text text-transparent bg-gradient-to-r from-primary to-tertiary">smart_toy</span>
                </div>
              </div>
              <div>
                <h2 class="text-lg font-bold text-on-surface m-0 bg-clip-text text-transparent bg-gradient-to-r from-on-surface to-on-surface-variant">TalentFlow 智能助手</h2>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                  </span>
                  <p class="text-xs font-medium text-emerald-600 m-0">上下文引擎已激活</p>
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <button class="w-9 h-9 rounded-lg border border-outline-variant/50 flex items-center justify-center text-on-surface-variant hover:bg-surface-container-low transition-colors">
                <span class="material-symbols-outlined text-[20px]">restart_alt</span>
              </button>
            </div>
          </div>

          <!-- Chat History -->
          <div ref="chatHistoryRef" class="flex-1 overflow-y-auto p-6 flex flex-col gap-6 no-scrollbar">
            
            <div class="flex justify-center sticky top-0 z-20">
              <span class="bg-surface-container-lowest/90 backdrop-blur-sm border border-outline-variant/40 text-on-surface-variant text-[11px] font-medium px-4 py-1.5 rounded-full shadow-sm">
                今天, 10:42 AM
              </span>
            </div>

            <!-- User Message -->
            <div class="flex justify-end group">
              <div class="bg-on-surface text-surface-container-lowest rounded-2xl rounded-tr-sm px-5 py-3.5 max-w-[80%] shadow-md">
                <p class="text-sm m-0">你能总结一下今年的公司休假政策吗？特别是关于假期结转的规定。</p>
              </div>
              <div class="w-8 h-8 rounded-full overflow-hidden border border-outline-variant ml-3 shadow-sm self-end shrink-0">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCrxqatEHDCXw88vrI_yjVcbb-S0UQKZYDPRmMJ2L8wJtEy0DYS0i0W4nE1L0U_Ks54MgkryE9ck-_dfxqWl3lHFBEY5lCh1xmnR1TuPSnQvchrafaVeAP8WibX2NHz92gFp_qqqTLrrVRtn_T0BSqFVOrSXUoOgk4-Be9JXUpzeU7aqHTP8-LZ7eeY_yQYWohSQOKQbzxch1Q-aF_ZrcDOImPm6QzaN1mjOAari_cfazlK_Bwy4H01sjsVz9SvVoTqomLOvf5bJdVO" alt="User" class="w-full h-full object-cover" />
              </div>
            </div>

            <!-- Intelligent process block -->
            <div class="flex justify-start pl-11 mb-2">
              <div class="bg-surface-container-low/50 rounded-xl p-4 border border-outline-variant/30 text-sm max-w-[85%] w-full shadow-inner">
                <div class="flex items-center gap-2 mb-3 text-primary text-xs font-bold uppercase tracking-wide">
                  <span class="material-symbols-outlined text-[16px] animate-spin" :style="{ animationDuration: '3s' }">memory</span> 
                  推理链路
                </div>
                
                <div class="relative h-20 w-full bg-surface-container-lowest/50 rounded-lg border border-outline-variant/30 overflow-hidden mb-3 p-3 flex justify-between items-center px-8">
                  <!-- Nodes -->
                  <div class="agent-progress-step agent-progress-step--first flex flex-col items-center gap-1 z-10">
                    <div class="agent-progress-node w-8 h-8 rounded-full bg-surface border-2 flex items-center justify-center">
                      <span class="material-symbols-outlined text-[16px]">shield</span>
                    </div>
                    <span class="text-[10px] font-medium">解析与审计</span>
                  </div>
                  
                  <div class="agent-progress-line agent-progress-line--first flex-1 h-0.5 mx-2" />
                  
                  <div class="agent-progress-step agent-progress-step--second flex flex-col items-center gap-1 z-10">
                    <div class="agent-progress-node w-8 h-8 rounded-full bg-surface border-2 flex items-center justify-center">
                      <span class="material-symbols-outlined text-[16px]">database</span>
                    </div>
                    <span class="text-[10px] font-medium">RAG 检索</span>
                  </div>
                  
                  <div class="agent-progress-line agent-progress-line--second flex-1 h-0.5 mx-2" />
                  
                  <div class="agent-progress-step agent-progress-step--third flex flex-col items-center gap-1 z-10">
                    <div class="agent-progress-node w-8 h-8 rounded-full bg-surface border-2 flex items-center justify-center scale-110">
                      <span class="material-symbols-outlined text-[16px]">psychology</span>
                    </div>
                    <span class="text-[10px] font-bold">综合分析</span>
                  </div>
                </div>

                <div class="agent-log-scroll space-y-1.5 font-mono text-[11px] text-on-surface-variant bg-surface-container-lowest/30 p-2.5 rounded border border-outline-variant/20">
                  <div class="flex items-start gap-2 opacity-75">
                    <span class="text-emerald-500 shrink-0">✔</span>
                    <span>[解析与审计] 提取意图: <code>POLICY_QUERY</code> | 用户权限 <code>policy.read</code> 验证成功</span>
                  </div>
                  <div class="flex items-start gap-2 opacity-75">
                    <span class="text-emerald-500 shrink-0">✔</span>
                    <span>[解析与审计] 审计服务记录数据读取操作，可解释安全通道已就绪</span>
                  </div>
                  <div class="flex items-start gap-2 opacity-75">
                    <span class="text-emerald-500 shrink-0">✔</span>
                    <span>[RAG 检索] 构建检索契约 <code>RetrievalQuery(active_only=True)</code> 并查询 ChromaDB 向量存储</span>
                  </div>
                  <div class="flex items-start gap-2 opacity-75">
                    <span class="text-emerald-500 shrink-0">✔</span>
                    <span>[RAG 检索] 成功召回匹配的制度文档片段，最高相似度评分 (relevance): 0.9431</span>
                  </div>
                  <div class="flex items-start gap-2 text-primary font-medium">
                    <span class="w-1.5 h-1.5 rounded-full bg-primary animate-pulse mt-1 shrink-0" />
                    <span>[综合分析] 载入 <code>KnowledgeChunk</code> [员工手册 (v2024.1)]，LLM 模型合规推理并生成可解释回答...</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Assistant message -->
            <div class="flex justify-start gap-3 relative z-10">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-tertiary/20 border border-primary/30 flex items-center justify-center text-primary shrink-0 mt-1 shadow-sm backdrop-blur-sm">
                <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
              </div>
              
              <div class="bg-surface-container-lowest border border-primary/30 rounded-2xl rounded-tl-sm p-6 max-w-[85%] ai-glow glass-card relative overflow-hidden group">
                <p class="text-sm text-on-surface m-0 mb-4 leading-relaxed relative z-10">
                  根据从政策中心检索到的最新 <strong>员工手册 (v2024.1)</strong>，以下是关于假期结转政策的摘要：
                </p>
                <ul class="list-disc pl-5 text-sm text-on-surface space-y-2 mb-5 relative z-10">
                  <li>员工最多可将 <strong>5 天未使用的年假</strong> 结转至下一日历年。</li>
                  <li>这些结转的假期必须在次年的 <strong>3月31日</strong> 之前使用。</li>
                  <li>任何在 3月31日 之前未使用的结转假期将被作废。</li>
                </ul>

                <!-- Source Citation -->
                <div class="bg-surface-container-low/70 rounded-xl p-4 border border-outline-variant/40 mt-2 relative overflow-hidden group-hover:border-primary/40 transition-colors">
                  <div class="absolute top-0 left-0 w-1 h-full bg-primary rounded-l-xl" />
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center gap-2">
                      <div class="p-1.5 bg-primary/10 rounded-lg text-primary">
                        <span class="material-symbols-outlined text-[18px]">menu_book</span>
                      </div>
                      <h4 class="text-sm font-semibold text-on-surface m-0">员工手册 2024</h4>
                    </div>
                    <div class="flex items-center gap-1.5 px-2 py-1 bg-emerald-100 border border-emerald-200 rounded-full text-emerald-700 font-medium text-[10px] assistant-conf-badge">
                      <span class="material-symbols-outlined text-[12px]">verified</span> 高置信度
                    </div>
                  </div>
                  
                  <button class="w-full flex items-center justify-between px-3 py-2 bg-surface-container-lowest hover:bg-primary/5 border border-outline-variant/40 hover:border-primary/40 rounded-lg transition-colors text-primary text-[13px] font-medium">
                    <span>查看完整政策文档</span>
                    <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                  </button>
                </div>
              </div>
            </div>

            <template v-for="turn in leaveTurns" :key="turn.id">
              <!-- Leave query user message -->
              <div class="flex justify-end group">
                <div class="bg-on-surface text-surface-container-lowest rounded-2xl rounded-tr-sm px-5 py-3.5 max-w-[80%] shadow-md">
                  <p class="text-sm m-0">{{ turn.prompt }}</p>
                </div>
                <div class="w-8 h-8 rounded-full overflow-hidden border border-outline-variant ml-3 shadow-sm self-end shrink-0">
                  <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCrxqatEHDCXw88vrI_yjVcbb-S0UQKZYDPRmMJ2L8wJtEy0DYS0i0W4nE1L0U_Ks54MgkryE9ck-_dfxqWl3lHFBEY5lCh1xmnR1TuPSnQvchrafaVeAP8WibX2NHz92gFp_qqqTLrrVRtn_T0BSqFVOrSXUoOgk4-Be9JXUpzeU7aqHTP8-LZ7eeY_yQYWohSQOKQbzxch1Q-aF_ZrcDOImPm6QzaN1mjOAari_cfazlK_Bwy4H01sjsVz9SvVoTqomLOvf5bJdVO" alt="User" class="w-full h-full object-cover" />
                </div>
              </div>

              <!-- Leave query auditable process -->
              <div class="flex justify-start pl-11 mb-2">
                <div class="bg-surface-container-low/50 rounded-xl p-4 border border-outline-variant/30 text-sm max-w-[85%] w-full shadow-inner">
                  <div class="flex items-center justify-between gap-3 mb-3">
                    <div class="flex items-center gap-2 text-primary text-xs font-bold uppercase tracking-wide">
                      <span
                        class="material-symbols-outlined text-[16px]"
                        :class="{ 'animate-spin': turn.status === 'loading' }"
                        :style="turn.status === 'loading' ? { animationDuration: '3s' } : undefined"
                      >memory</span>
                      推理链路
                    </div>
                    <span
                      class="text-[10px] font-semibold"
                      :class="turn.status === 'error' ? 'text-red-600' : turn.status === 'success' ? 'text-emerald-600' : 'text-primary'"
                    >{{ leaveTurnStatusLabel(turn) }}</span>
                  </div>

                  <div class="relative h-20 w-full bg-surface-container-lowest/50 rounded-lg border border-outline-variant/30 overflow-hidden mb-3 p-3 flex justify-between items-center px-8">
                    <div class="agent-progress-step agent-progress-step--first flex flex-col items-center gap-1 z-10">
                      <div class="agent-progress-node w-8 h-8 rounded-full bg-surface border-2 flex items-center justify-center">
                        <span class="material-symbols-outlined text-[16px]">manage_search</span>
                      </div>
                      <span class="text-[10px] font-medium">请求解析</span>
                    </div>

                    <div class="agent-progress-line agent-progress-line--first flex-1 h-0.5 mx-2" />

                    <div class="agent-progress-step agent-progress-step--second flex flex-col items-center gap-1 z-10">
                      <div class="agent-progress-node w-8 h-8 rounded-full bg-surface border-2 flex items-center justify-center">
                        <span class="material-symbols-outlined text-[16px]">database</span>
                      </div>
                      <span class="text-[10px] font-medium">数据查询</span>
                    </div>

                    <div class="agent-progress-line agent-progress-line--second flex-1 h-0.5 mx-2" />

                    <div
                      class="agent-progress-step agent-progress-step--third flex flex-col items-center gap-1 z-10"
                      @animationend.self="markLeaveProgressComplete(turn)"
                    >
                      <div class="agent-progress-node w-8 h-8 rounded-full bg-surface border-2 flex items-center justify-center scale-110">
                        <span class="material-symbols-outlined text-[16px]">table_view</span>
                      </div>
                      <span class="text-[10px] font-bold">结果整理</span>
                    </div>
                  </div>

                  <div v-auto-scroll class="agent-log-scroll space-y-1.5 font-mono text-[11px] text-on-surface-variant bg-surface-container-lowest/30 p-2.5 rounded border border-outline-variant/20">
                    <div
                      v-for="(log, logIndex) in turn.logs.slice(0, turn.visibleLogCount)"
                      :key="`${turn.id}-log-${logIndex}`"
                      class="agent-log-entry flex items-start gap-2"
                      @animationend.self="handleLeaveLogAnimationEnd(turn, logIndex)"
                    >
                      <span class="shrink-0" :class="log.includes('失败') ? 'text-red-500' : 'text-emerald-500'">•</span>
                      <span :class="{ 'text-red-600 font-medium': log.includes('失败') }">{{ log }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Leave query result -->
              <div v-if="turn.status !== 'loading' && turn.progressComplete && turn.logsComplete" class="flex justify-start gap-3 relative z-10">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-tertiary/20 border border-primary/30 flex items-center justify-center text-primary shrink-0 mt-1 shadow-sm backdrop-blur-sm">
                  <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
                </div>

                <div class="bg-surface-container-lowest border border-primary/30 rounded-2xl rounded-tl-sm p-6 max-w-[85%] w-full min-w-0 ai-glow glass-card relative overflow-hidden">
                  <p v-if="turn.status === 'error'" class="text-sm text-red-600 m-0 leading-relaxed relative z-10">
                    剩余假期查询失败：{{ turn.errorMessage }}
                  </p>
                  <p v-else-if="turn.balances.length === 0" class="text-sm text-on-surface m-0 leading-relaxed relative z-10">
                    当前年度暂无可用的假期余额数据。
                  </p>
                  <template v-else>
                    <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-5 relative z-10">
                      <div>
                        <h3 class="text-lg font-bold text-on-surface m-0">{{ leaveResultYear(turn) }} 年度假期余额</h3>
                        <p class="text-xs text-on-surface-variant m-0 mt-1.5">已查询到您当前年度的假期账户信息</p>
                      </div>
                      <span class="self-start inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-[11px] font-semibold text-emerald-700 leave-query-success-badge">
                        <span class="material-symbols-outlined text-[14px]">check_circle</span>
                        查询成功
                      </span>
                    </div>

                    <!-- 单一类型按三个指标展示，多个类型按类型拆分，避免跨单位汇总。 -->
                    <div v-if="turn.balances.length === 1" class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5 relative z-10">
                      <div
                        v-for="overview in singleBalanceOverview(turn.balances[0])"
                        :key="overview.label"
                        class="rounded-xl border border-outline-variant/40 bg-surface-container-low/50 p-3.5"
                      >
                        <p class="text-[11px] font-medium text-on-surface-variant m-0">{{ overview.label }}</p>
                        <p class="mt-2 mb-0 text-lg font-bold tabular-nums" :class="overview.emphasis ? 'text-primary' : 'text-on-surface'">
                          {{ overview.value }}
                        </p>
                      </div>
                    </div>

                    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-5 relative z-10">
                      <div
                        v-for="balance in turn.balances"
                        :key="`overview-${balance.id}`"
                        class="rounded-xl border border-outline-variant/40 bg-surface-container-low/50 p-3.5"
                      >
                        <div class="flex items-center gap-2 mb-3">
                          <span class="material-symbols-outlined text-[18px] text-primary">{{ leaveTypeIcon(balance.leave_type) }}</span>
                          <span class="text-sm font-semibold text-on-surface">{{ leaveTypeLabel(balance.leave_type) }}</span>
                        </div>
                        <div class="grid grid-cols-3 gap-2">
                          <div>
                            <p class="text-[10px] text-on-surface-variant m-0">总额度</p>
                            <p class="text-xs font-semibold text-on-surface m-0 mt-1 tabular-nums">{{ formatLeaveAmount(balance.total_days) }} {{ leaveUnit(balance.leave_type) }}</p>
                          </div>
                          <div>
                            <p class="text-[10px] text-on-surface-variant m-0">已使用</p>
                            <p class="text-xs font-semibold text-on-surface m-0 mt-1 tabular-nums">{{ formatLeaveAmount(balance.used_days) }} {{ leaveUnit(balance.leave_type) }}</p>
                          </div>
                          <div>
                            <p class="text-[10px] text-on-surface-variant m-0">当前剩余</p>
                            <p class="text-xs font-bold text-primary m-0 mt-1 tabular-nums">{{ formatLeaveAmount(remainingLeave(balance)) }} {{ leaveUnit(balance.leave_type) }}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="leave-balance-table-wrap rounded-xl border border-outline-variant/40 bg-surface-container-lowest overflow-x-auto relative z-10">
                      <table class="w-full min-w-[720px] border-collapse text-sm text-on-surface">
                        <thead class="bg-surface-container-low text-on-surface-variant">
                          <tr>
                            <th class="px-4 py-3 text-left font-semibold">假期类型</th>
                            <th class="px-4 py-3 text-left font-semibold">额度使用情况</th>
                            <th class="px-4 py-3 text-left font-semibold">当前剩余</th>
                            <th class="px-4 py-3 text-center font-semibold">状态</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="balance in turn.balances" :key="balance.id" class="h-20 border-t border-outline-variant/30 transition-colors hover:bg-primary/5">
                            <td class="px-4 py-3">
                              <div class="flex items-center gap-3">
                                <div class="w-9 h-9 rounded-lg border border-primary/15 bg-primary/5 text-primary flex items-center justify-center shrink-0">
                                  <span class="material-symbols-outlined text-[19px]">{{ leaveTypeIcon(balance.leave_type) }}</span>
                                </div>
                                <div>
                                  <p class="text-sm font-semibold text-on-surface m-0">{{ leaveTypeLabel(balance.leave_type) }}</p>
                                  <p class="text-[11px] text-on-surface-variant m-0 mt-1">{{ leaveTypeSubtitle(balance.leave_type) }}</p>
                                </div>
                              </div>
                            </td>
                            <td class="px-4 py-3 min-w-[230px]">
                              <p class="text-xs text-on-surface m-0 tabular-nums">
                                已使用 {{ formatLeaveAmount(balance.used_days) }} / {{ formatLeaveAmount(balance.total_days) }} {{ leaveUnit(balance.leave_type) }}
                              </p>
                              <div class="w-full h-1.5 rounded-full bg-surface-variant overflow-hidden mt-2">
                                <div class="h-full rounded-full bg-primary" :style="{ width: `${leaveUsageRate(balance)}%` }" />
                              </div>
                              <p class="text-[10px] text-on-surface-variant m-0 mt-1.5">使用率 {{ leaveUsageRate(balance) }}%</p>
                            </td>
                            <td class="px-4 py-3 min-w-[130px]">
                              <p class="text-base font-bold text-primary m-0 tabular-nums">{{ formatLeaveAmount(remainingLeave(balance)) }} {{ leaveUnit(balance.leave_type) }}</p>
                              <p class="text-[10px] text-on-surface-variant m-0 mt-1">可用余额</p>
                            </td>
                            <td class="px-4 py-3 text-center">
                              <span class="inline-flex whitespace-nowrap rounded-full border px-2.5 py-1 text-[11px] font-semibold" :class="leaveBalanceStatus(balance).className">
                                {{ leaveBalanceStatus(balance).label }}
                              </span>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>

                    <div class="mt-4 flex flex-col gap-1.5 text-[10px] text-on-surface-variant relative z-10">
                      <p class="m-0">数据来源：员工假期账户 · 查询时间：{{ turn.completedAt }}</p>
                      <p class="m-0">剩余额度以人力资源部门最终审核记录为准。</p>
                    </div>
                  </template>
                </div>
              </div>
            </template>
          </div>
          <!-- Input Area -->
          <div class="p-5 border-t border-outline-variant/40 bg-surface-container-lowest/80 backdrop-blur-xl z-20">
            <!-- Suggestions -->
            <div class="flex gap-2 overflow-x-auto no-scrollbar pb-3 mb-2">
              <button
                type="button"
                class="whitespace-nowrap px-4 py-2 rounded-xl border border-outline-variant/60 bg-surface-container-lowest/50 text-on-surface text-sm hover:border-primary/50 hover:bg-primary/5 hover:text-primary transition-all flex items-center gap-2 shadow-sm font-medium disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:border-outline-variant/60 disabled:hover:bg-surface-container-lowest/50 disabled:hover:text-on-surface"
                :disabled="leaveQueryLoading"
                @click="handleLeaveQuery"
              >
                <span class="material-symbols-outlined text-[18px] text-primary/70">beach_access</span> 剩余假期查询
              </button>
              <button class="whitespace-nowrap px-4 py-2 rounded-xl border border-outline-variant/60 bg-surface-container-lowest/50 text-on-surface text-sm hover:border-primary/50 hover:bg-primary/5 hover:text-primary transition-all flex items-center gap-2 shadow-sm font-medium">
                <span class="material-symbols-outlined text-[18px] text-emerald-600/70">payments</span> 查看最新工资单
              </button>
            </div>
            
            <div class="relative group">
              <div class="absolute -inset-0.5 bg-gradient-to-r from-primary/30 to-tertiary/30 rounded-2xl blur opacity-30 group-hover:opacity-60 transition duration-500" />
              <div class="relative flex items-center bg-surface-container-lowest border border-outline-variant/50 rounded-2xl shadow-inner overflow-hidden focus-within:ring-1 focus-within:ring-primary focus-within:border-primary transition-all">
                <div class="pl-4 pr-2 flex items-center text-primary">
                  <span class="material-symbols-outlined text-[24px]">auto_awesome</span>
                </div>
                <input 
                  type="text" 
                  placeholder="问问智能助手任何事..." 
                  class="w-full h-14 bg-transparent border-none focus:ring-0 text-sm text-on-surface placeholder:text-outline/60 px-2 outline-none"
                />
                <div class="pr-2 flex gap-1">
                  <button class="w-10 h-10 rounded-xl flex items-center justify-center text-outline hover:text-on-surface hover:bg-surface-container-low transition-colors">
                    <span class="material-symbols-outlined text-[20px]">mic</span>
                  </button>
                  <button class="w-12 h-10 rounded-xl bg-gradient-to-r from-primary to-primary-container text-white flex items-center justify-center hover:shadow-lg hover:shadow-primary/30 transition-all ml-1">
                    <span class="material-symbols-outlined text-[20px]">send</span>
                  </button>
                </div>
              </div>
            </div>
            <div class="text-center mt-3">
              <span class="text-[10px] text-outline/70 font-medium">智能建议可能存在偏差，请核实重要信息。</span>
            </div>
          </div>
        </div>

        <!-- Right Sidebar Dashboard (Desktop) -->
        <div class="hidden xl:flex w-[340px] flex-col gap-5 z-10">
          <div class="bg-gradient-to-br from-primary/5 to-tertiary/5 rounded-2xl border border-primary/20 shadow-lg p-5 relative overflow-hidden glass-card">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined text-[18px]">insights</span>
              </div>
              <h3 class="text-base font-semibold text-on-surface m-0">智能洞察</h3>
            </div>
            <p class="text-[13px] text-on-surface-variant m-0 leading-relaxed">
              根据您最近的查询，您可能正在计划休假。您还有 <strong class="text-primary font-semibold">14.5 天</strong> 余额。如果您在即将到来的假期中使用 5 天，明年您仍可结转 <strong class="text-primary font-semibold">4.5 天</strong>。
            </p>
            <button class="mt-4 w-full py-2 px-4 bg-surface-container-lowest border border-primary/30 rounded-lg text-primary text-xs font-semibold hover:bg-primary/5 transition-colors flex items-center justify-center gap-2">
              <span class="material-symbols-outlined text-[16px]">edit_calendar</span> 起草休假申请
            </button>
          </div>

          <div class="bg-surface-container-lowest/80 rounded-2xl border border-outline-variant/40 shadow-lg p-5 glass-card">
            <h3 class="text-base font-semibold text-on-surface m-0 mb-5 flex items-center gap-2">
              <span class="material-symbols-outlined text-outline text-[20px]">dashboard</span> 我的仪表板
            </h3>
            
            <div class="space-y-5">
              <div>
                <div class="flex justify-between items-end mb-2">
                  <div>
                    <span class="text-[10px] text-outline uppercase tracking-wider font-bold block mb-1">剩余年假</span>
                    <div class="flex items-baseline gap-1">
                      <span class="text-3xl font-bold text-on-surface leading-none">14.5</span>
                      <span class="text-xs text-on-surface-variant font-medium">/ 20 天</span>
                    </div>
                  </div>
                  <div class="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center text-primary-container">
                    <span class="material-symbols-outlined text-[20px]">flight_takeoff</span>
                  </div>
                </div>
                <div class="w-full bg-surface-variant h-2 rounded-full mt-3 overflow-hidden">
                  <div class="bg-gradient-to-r from-primary to-tertiary h-full rounded-full" :style="{ width: '72%' }" />
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue';
import { ApiClientError } from '../shared/api/apiClient';
import { fetchLeaveOverview, type LeaveBalanceItem } from '../shared/api/modules/employee';

type LeaveAssistantTurnStatus = 'loading' | 'success' | 'error';

interface LeaveAssistantTurn {
  id: string;
  prompt: string;
  status: LeaveAssistantTurnStatus;
  logs: string[];
  balances: LeaveBalanceItem[];
  visibleLogCount: number;
  logAnimationActive: boolean;
  logsComplete: boolean;
  progressComplete: boolean;
  completedAt?: string;
  errorMessage?: string;
}

const chatHistoryRef = ref<HTMLElement | null>(null);
const leaveTurns = ref<LeaveAssistantTurn[]>([]);
let leaveTurnSequence = 0;

const leaveQueryLoading = computed(() => leaveTurns.value.some(
  (turn) => turn.status === 'loading' || !turn.logsComplete || !turn.progressComplete,
));
const leaveTypeOrder: Record<string, number> = { ANNUAL: 0, SICK: 1, COMP_TIME: 2 };

const vAutoScroll = {
  mounted(element: HTMLElement) {
    element.scrollTop = element.scrollHeight;
  },
  updated(element: HTMLElement) {
    element.scrollTop = element.scrollHeight;
  },
};

function leaveTurnStatusLabel(turn: LeaveAssistantTurn): string {
  if (turn.status === 'loading') return '正在查询';
  if (!turn.logsComplete || !turn.progressComplete) return '正在整理';
  return turn.status === 'success' ? '查询完成' : '查询失败';
}

function leaveTypeLabel(type: string): string {
  return { ANNUAL: '年假', SICK: '带薪病假', COMP_TIME: '调休' }[type] ?? type;
}

function leaveTypeSubtitle(type: string): string {
  return {
    ANNUAL: '年度带薪休假',
    SICK: '员工带薪病假额度',
    COMP_TIME: '加班调休可用时长',
  }[type] ?? '其他假期账户';
}

function leaveTypeIcon(type: string): string {
  return {
    ANNUAL: 'flight_takeoff',
    SICK: 'medical_services',
    COMP_TIME: 'schedule',
  }[type] ?? 'event_available';
}

function leaveUnit(type: string): string {
  return type === 'COMP_TIME' ? '小时' : '天';
}

function remainingLeave(balance: LeaveBalanceItem): number {
  return Math.max(0, Number(balance.total_days) - Number(balance.used_days));
}

function formatLeaveAmount(value: number): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? amount.toLocaleString('zh-CN', { maximumFractionDigits: 2 }) : '—';
}

function leaveResultYear(turn: LeaveAssistantTurn): number {
  return Number(turn.balances[0]?.year ?? new Date().getFullYear());
}

function singleBalanceOverview(balance?: LeaveBalanceItem): Array<{ label: string; value: string; emphasis: boolean }> {
  if (!balance) return [];
  const unit = leaveUnit(balance.leave_type);
  return [
    { label: '总额度', value: `${formatLeaveAmount(balance.total_days)} ${unit}`, emphasis: false },
    { label: '已使用', value: `${formatLeaveAmount(balance.used_days)} ${unit}`, emphasis: false },
    { label: '当前剩余', value: `${formatLeaveAmount(remainingLeave(balance))} ${unit}`, emphasis: true },
  ];
}

function leaveUsageRate(balance: LeaveBalanceItem): number {
  const total = Number(balance.total_days);
  const used = Number(balance.used_days);
  return total > 0
    ? Math.min(100, Math.max(0, Math.round(used * 100 / total)))
    : 0;
}

function leaveBalanceStatus(balance: LeaveBalanceItem): { label: string; className: string } {
  const total = Number(balance.total_days);
  const remaining = remainingLeave(balance);
  if (total <= 0) return { label: '暂无额度', className: 'leave-status--empty' };
  if (remaining <= 0) return { label: '已用完', className: 'leave-status--exhausted' };
  if (remaining / total <= 0.2) return { label: '即将用完', className: 'leave-status--low' };
  return { label: '余额充足', className: 'leave-status--sufficient' };
}

function formatLeaveQueryTime(date: Date): string {
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

function safeLeaveErrorMessage(error: unknown): string {
  if (error instanceof ApiClientError && error.message.trim()) return error.message;
  return '请求未能完成，请稍后重试。';
}

async function scrollChatToLatest(): Promise<void> {
  await nextTick();
  const chatHistory = chatHistoryRef.value;
  if (!chatHistory) return;
  chatHistory.scrollTo({ top: chatHistory.scrollHeight, behavior: 'smooth' });
}

function revealNextLeaveLog(turn: LeaveAssistantTurn): void {
  if (turn.logAnimationActive) return;
  if (turn.visibleLogCount < turn.logs.length) {
    turn.visibleLogCount += 1;
    turn.logAnimationActive = true;
    void scrollChatToLatest();
    return;
  }
  if (turn.status !== 'loading') turn.logsComplete = true;
}

function handleLeaveLogAnimationEnd(turn: LeaveAssistantTurn, logIndex: number): void {
  if (logIndex !== turn.visibleLogCount - 1) return;
  turn.logAnimationActive = false;
  revealNextLeaveLog(turn);
  void scrollChatToLatest();
}

function markLeaveProgressComplete(turn: LeaveAssistantTurn): void {
  turn.progressComplete = true;
  void scrollChatToLatest();
}

async function handleLeaveQuery(): Promise<void> {
  if (leaveQueryLoading.value) return;

  leaveTurnSequence += 1;
  const turn = reactive<LeaveAssistantTurn>({
    id: `leave-turn-${leaveTurnSequence}`,
    prompt: '请查询我当前年度的剩余假期。',
    status: 'loading',
    logs: [
      '[请求解析] 已识别快捷操作：剩余假期查询',
      '[身份上下文] 正在使用当前登录用户身份',
      '[接口请求] 正在查询本人当前年度假期余额',
      '[数据查询] 调用 /employees/me/leave-overview',
    ],
    balances: [],
    visibleLogCount: 1,
    logAnimationActive: true,
    logsComplete: false,
    progressComplete: false,
  });

  leaveTurns.value.push(turn);
  await scrollChatToLatest();

  try {
    const overview = await fetchLeaveOverview();
    turn.balances = [...overview.balances].sort(
      (left, right) => (leaveTypeOrder[left.leave_type] ?? Number.MAX_SAFE_INTEGER) - (leaveTypeOrder[right.leave_type] ?? Number.MAX_SAFE_INTEGER),
    );
    turn.logs.push(`[数据返回] 已获取 ${overview.balances.length} 条假期余额记录`);
    if (overview.balances.length > 0) {
      turn.logs.push('[结果整理] 正在计算各类假期剩余额度');
      turn.logs.push('[结果生成] 已生成剩余假期表格');
    } else {
      turn.logs.push('[结果生成] 当前年度暂无可用的假期余额数据');
    }
    turn.completedAt = formatLeaveQueryTime(new Date());
    turn.status = 'success';
    revealNextLeaveLog(turn);
  } catch (error: unknown) {
    const errorMessage = safeLeaveErrorMessage(error);
    turn.errorMessage = errorMessage;
    turn.logs.push(`[接口失败] 剩余假期查询失败：${errorMessage}`);
    turn.status = 'error';
    revealNextLeaveLog(turn);
  } finally {
    await scrollChatToLatest();
  }
}
</script>

<style scoped>
/* 每张推理卡片按“节点停留发光 2 秒 → 连接线”顺序播放一次。 */
.agent-progress-step {
  --agent-step-delay: 0s;
  color: #94a3b8;
  animation: agent-progress-step-activate 2s ease-out var(--agent-step-delay) 1 forwards;
}

.agent-progress-step--first { --agent-step-delay: 0s; }
.agent-progress-step--second { --agent-step-delay: 2.4s; }
.agent-progress-step--third { --agent-step-delay: 4.8s; }

.agent-progress-node {
  border-color: currentColor;
  animation: agent-progress-node-glow 2s ease-in-out var(--agent-step-delay) 1 forwards;
}

.agent-progress-line {
  --agent-progress-delay: 2s;
  position: relative;
  overflow: hidden;
  background: rgba(148, 163, 184, 0.35);
}

.agent-progress-line--first { --agent-progress-delay: 2s; }
.agent-progress-line--second { --agent-progress-delay: 4.4s; }

.agent-progress-line::after {
  content: '';
  position: absolute;
  inset: 0;
  background: #10b981;
  transform: scaleX(0);
  transform-origin: left;
  animation: agent-progress-fill 0.4s ease-out var(--agent-progress-delay) 1 forwards;
}

@keyframes agent-progress-step-activate {
  0% { color: #94a3b8; }
  10%, 100% { color: #10b981; }
}

@keyframes agent-progress-node-glow {
  0% { box-shadow: 0 0 0 rgba(16, 185, 129, 0); }
  15%, 85% { box-shadow: 0 0 14px rgba(16, 185, 129, 0.75); }
  100% { box-shadow: 0 0 9px rgba(16, 185, 129, 0.5); }
}

@keyframes agent-progress-fill {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

.agent-log-entry {
  opacity: 0;
  transform: translateY(4px);
  animation: agent-log-reveal 1s ease-out 0s 1 forwards;
}

@keyframes agent-log-reveal {
  0% { opacity: 0; transform: translateY(4px); }
  18%, 100% { opacity: 1; transform: translateY(0); }
}

.agent-log-scroll {
  height: 112px;
  min-height: 112px;
  max-height: 112px;
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
}

.leave-balance-table-wrap {
  max-width: 100%;
  overscroll-behavior-x: contain;
}

.leave-status--sufficient {
  border-color: #bbf7d0;
  background: #f0fdf4;
  color: #15803d;
}

.leave-status--low {
  border-color: #fed7aa;
  background: #fff7ed;
  color: #c2410c;
}

.leave-status--exhausted {
  border-color: #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}

.leave-status--empty {
  border-color: #d1d5db;
  background: #f3f4f6;
  color: #6b7280;
}

/* 深色模式适配 */
[data-theme="dark"] .assistant-conf-badge { background-color: #052e16 !important; border-color: #166534 !important; color: #86efac !important; }
:global([data-theme="dark"]) .leave-query-success-badge,
:global([data-theme="dark"]) .leave-status--sufficient { background-color: #052e16 !important; border-color: #166534 !important; color: #86efac !important; }
:global([data-theme="dark"]) .leave-status--low { background-color: #431407 !important; border-color: #9a3412 !important; color: #fdba74 !important; }
:global([data-theme="dark"]) .leave-status--exhausted { background-color: #450a0a !important; border-color: #991b1b !important; color: #fca5a5 !important; }
:global([data-theme="dark"]) .leave-status--empty { background-color: #1f2937 !important; border-color: #4b5563 !important; color: #d1d5db !important; }
</style>
