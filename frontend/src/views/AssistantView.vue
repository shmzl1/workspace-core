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
                <p class="text-xs font-medium text-emerald-600 m-0">数据助手已就绪</p>
              </div>
            </div>
          </div>
          <button
            type="button"
            class="w-9 h-9 rounded-lg border border-outline-variant/50 flex items-center justify-center text-on-surface-variant hover:bg-surface-container-low transition-colors disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="queryActive || turns.length === 0"
            title="清空当前对话"
            @click="clearConversation"
          >
            <span class="material-symbols-outlined text-[20px]">restart_alt</span>
          </button>
        </div>

        <!-- Chat History -->
        <div ref="chatHistoryRef" class="flex-1 overflow-y-auto p-6 flex flex-col gap-6 no-scrollbar">
          <div class="flex justify-center sticky top-0 z-20">
            <span class="bg-surface-container-lowest/90 backdrop-blur-sm border border-outline-variant/40 text-on-surface-variant text-[11px] font-medium px-4 py-1.5 rounded-full shadow-sm">
              {{ conversationTimeLabel }}
            </span>
          </div>

          <!-- Initial welcome contains no business values. -->
          <div class="flex justify-start gap-3 relative z-10">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-tertiary/20 border border-primary/30 flex items-center justify-center text-primary shrink-0 mt-1 shadow-sm backdrop-blur-sm">
              <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
            </div>
            <div class="bg-surface-container-lowest border border-primary/30 rounded-2xl rounded-tl-sm p-5 max-w-[85%] ai-glow glass-card relative overflow-hidden">
              <p class="text-sm font-semibold text-on-surface m-0">您好，我可以查询您的假期余额、本人薪资与考勤影响因素，以及公司政策制度。</p>
              <p class="text-xs text-on-surface-variant m-0 mt-2 leading-relaxed">请输入自然语言问题。业务结果均来自现有数据库接口，不会在前端推算正式薪资或编写政策正文。</p>
            </div>
          </div>

          <template v-for="turn in turns" :key="turn.id">
            <!-- User message -->
            <div class="flex justify-end group">
              <div class="bg-on-surface text-surface-container-lowest rounded-2xl rounded-tr-sm px-5 py-3.5 max-w-[80%] shadow-md">
                <p class="text-sm m-0 whitespace-pre-wrap break-words">{{ turn.prompt }}</p>
              </div>
              <div class="w-8 h-8 rounded-full border border-outline-variant ml-3 shadow-sm self-end shrink-0 bg-surface-container-low flex items-center justify-center text-on-surface-variant">
                <span class="material-symbols-outlined text-[19px]">person</span>
              </div>
            </div>

            <!-- Auditable process -->
            <div class="flex justify-start pl-11 mb-2">
              <div class="bg-surface-container-low/50 rounded-xl p-4 border border-outline-variant/30 text-sm max-w-[85%] w-full shadow-inner">
                <div class="flex items-center justify-between gap-3 mb-3">
                  <div class="flex items-center gap-2 text-primary text-xs font-bold uppercase tracking-wide">
                    <span
                      class="material-symbols-outlined text-[16px]"
                      :class="{ 'animate-spin': !turn.requestComplete }"
                      :style="!turn.requestComplete ? { animationDuration: '3s' } : undefined"
                    >memory</span>
                    可审计过程
                  </div>
                  <span
                    class="text-[10px] font-semibold"
                    :class="turn.status === 'error' ? 'text-red-600' : canShowResult(turn) ? 'text-emerald-600' : 'text-primary'"
                  >{{ turnStatusLabel(turn) }}</span>
                </div>

                <div class="relative h-20 w-full bg-surface-container-lowest/50 rounded-lg border border-outline-variant/30 overflow-hidden mb-3 p-3 flex justify-between items-center px-4 sm:px-8">
                  <div class="agent-progress-step agent-progress-step--first flex flex-col items-center gap-1 z-10">
                    <div class="agent-progress-node w-8 h-8 rounded-full bg-surface border-2 flex items-center justify-center">
                      <span class="material-symbols-outlined text-[16px]">manage_search</span>
                    </div>
                    <span class="text-[10px] font-medium">问题理解</span>
                  </div>

                  <div class="agent-progress-line agent-progress-line--first flex-1 h-0.5 mx-2" />

                  <div class="agent-progress-step agent-progress-step--second flex flex-col items-center gap-1 z-10">
                    <div class="agent-progress-node w-8 h-8 rounded-full bg-surface border-2 flex items-center justify-center">
                      <span class="material-symbols-outlined text-[16px]">database</span>
                    </div>
                    <span class="text-[10px] font-medium">业务处理</span>
                  </div>

                  <div class="agent-progress-line agent-progress-line--second flex-1 h-0.5 mx-2" />

                  <div
                    class="agent-progress-step agent-progress-step--third flex flex-col items-center gap-1 z-10"
                    @animationend.self="markProgressComplete(turn)"
                  >
                    <div class="agent-progress-node w-8 h-8 rounded-full bg-surface border-2 flex items-center justify-center scale-110">
                      <span class="material-symbols-outlined text-[16px]">view_quilt</span>
                    </div>
                    <span class="text-[10px] font-bold">结果整理</span>
                  </div>
                </div>

                <div v-auto-scroll class="agent-log-scroll space-y-1.5 font-mono text-[11px] text-on-surface-variant bg-surface-container-lowest/30 p-2.5 rounded border border-outline-variant/20">
                  <div
                    v-for="(log, logIndex) in turn.logs.slice(0, turn.visibleLogCount)"
                    :key="`${turn.id}-log-${logIndex}`"
                    class="agent-log-entry flex items-start gap-2"
                    @animationend.self="handleLogAnimationEnd(turn, logIndex)"
                  >
                    <span class="shrink-0" :class="isErrorLog(log) ? 'text-red-500' : 'text-emerald-500'">•</span>
                    <span :class="{ 'text-red-600 font-medium': isErrorLog(log) }">{{ log }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Result: all three completion gates are intentionally explicit. -->
            <div
              v-if="turn.requestComplete && turn.progressComplete && turn.logsComplete"
              class="flex justify-start gap-3 relative z-10"
            >
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-tertiary/20 border border-primary/30 flex items-center justify-center text-primary shrink-0 mt-1 shadow-sm backdrop-blur-sm">
                <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
              </div>

              <div class="bg-surface-container-lowest border border-primary/30 rounded-2xl rounded-tl-sm p-6 max-w-[85%] w-full min-w-0 ai-glow glass-card relative overflow-hidden">
                <div v-if="turn.status === 'error'" class="flex items-start gap-3">
                  <span class="material-symbols-outlined text-red-500 text-[22px]">error</span>
                  <div>
                    <p class="text-sm font-semibold text-red-600 m-0">{{ intentLabel(turn.intent) }}处理失败</p>
                    <p class="text-sm text-on-surface-variant m-0 mt-1.5 leading-relaxed">{{ turn.errorMessage }}</p>
                  </div>
                </div>

                <!-- Normal chat uses text interpolation only; model HTML is never rendered. -->
                <template v-else-if="turn.intent === 'CHAT'">
                  <p class="text-sm text-on-surface m-0 whitespace-pre-wrap break-words leading-relaxed">
                    {{ turn.assistantReply }}
                  </p>
                </template>

                <!-- Leave result keeps the existing cards, table and progress presentation. -->
                <template v-else-if="turn.intent === 'LEAVE'">
                  <p v-if="leaveBalances(turn).length === 0" class="text-sm text-on-surface m-0 leading-relaxed relative z-10">
                    {{ leaveResultYear(turn) }} 年度暂无可用的假期余额数据。
                  </p>
                  <template v-else>
                    <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-5 relative z-10">
                      <div>
                        <h3 class="text-lg font-bold text-on-surface m-0">{{ leaveResultYear(turn) }} 年度假期余额</h3>
                        <p class="text-xs text-on-surface-variant m-0 mt-1.5">已查询到您所选年度的假期账户信息</p>
                      </div>
                      <span class="self-start inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-[11px] font-semibold text-emerald-700 leave-query-success-badge">
                        <span class="material-symbols-outlined text-[14px]">check_circle</span>
                        查询成功
                      </span>
                    </div>

                    <div v-if="leaveBalances(turn).length === 1" class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5 relative z-10">
                      <div
                        v-for="overview in singleBalanceOverview(leaveBalances(turn)[0])"
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
                        v-for="balance in leaveBalances(turn)"
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
                          <tr v-for="balance in leaveBalances(turn)" :key="balance.id" class="h-20 border-t border-outline-variant/30 transition-colors hover:bg-primary/5">
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
                      <p class="m-0">数据来源：员工假期账户数据库接口 · 查询时间：{{ turn.completedAt }}</p>
                      <p class="m-0">剩余额度以人力资源部门最终审核记录为准。</p>
                    </div>
                  </template>
                </template>

                <!-- Payroll result -->
                <template v-else-if="turn.intent === 'PAYROLL' && turn.payrollResult">
                  <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-5">
                    <div>
                      <h3 class="text-lg font-bold text-on-surface m-0">{{ turn.payrollResult.period.label }}薪资与考勤影响因素</h3>
                      <p class="text-xs text-on-surface-variant m-0 mt-1.5">仅展示数据库记录，不在前端计算实发工资或扣款金额</p>
                    </div>
                    <span class="self-start inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-[11px] font-semibold text-primary">
                      <span class="material-symbols-outlined text-[14px]">verified</span>
                      数据库记录
                    </span>
                  </div>

                  <div class="rounded-xl border border-primary/20 bg-gradient-to-br from-primary/5 to-tertiary/5 p-4 mb-5">
                    <div class="flex items-center gap-2 mb-4">
                      <span class="material-symbols-outlined text-primary text-[20px]">account_balance_wallet</span>
                      <h4 class="text-sm font-bold text-on-surface m-0">薪资概览</h4>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                      <div class="rounded-lg border border-outline-variant/30 bg-surface-container-lowest/70 p-3">
                        <p class="text-[10px] text-on-surface-variant m-0">基础月薪</p>
                        <p class="text-lg font-bold text-primary m-0 mt-1.5 tabular-nums">{{ formatSalaryAmount(turn.payrollResult.salary.base_salary) }}</p>
                      </div>
                      <div class="rounded-lg border border-outline-variant/30 bg-surface-container-lowest/70 p-3">
                        <p class="text-[10px] text-on-surface-variant m-0">币种</p>
                        <p class="text-sm font-semibold text-on-surface m-0 mt-2">{{ turn.payrollResult.salary.currency || '—' }}</p>
                      </div>
                      <div class="rounded-lg border border-outline-variant/30 bg-surface-container-lowest/70 p-3">
                        <p class="text-[10px] text-on-surface-variant m-0">生效日期</p>
                        <p class="text-sm font-semibold text-on-surface m-0 mt-2">{{ formatDate(turn.payrollResult.salary.effective_from) }}</p>
                      </div>
                      <div class="rounded-lg border border-outline-variant/30 bg-surface-container-lowest/70 p-3">
                        <p class="text-[10px] text-on-surface-variant m-0">截止日期</p>
                        <p class="text-sm font-semibold text-on-surface m-0 mt-2">{{ turn.payrollResult.salary.effective_to ? formatDate(turn.payrollResult.salary.effective_to) : '长期有效' }}</p>
                      </div>
                    </div>
                  </div>

                  <div class="rounded-xl border border-outline-variant/40 bg-surface-container-low/30 p-4 mb-4">
                    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
                      <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-primary text-[20px]">event_note</span>
                        <h4 class="text-sm font-bold text-on-surface m-0">考勤影响因素</h4>
                      </div>
                      <span class="text-[11px] font-semibold" :class="payrollRiskCount(turn.payrollResult.attendance) > 0 ? 'text-orange-600' : 'text-emerald-600'">
                        {{ payrollRiskSummary(turn.payrollResult.attendance) }}
                      </span>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      <div
                        v-for="factor in attendanceFactors(turn.payrollResult.attendance)"
                        :key="factor.key"
                        class="rounded-xl border border-outline-variant/40 bg-surface-container-lowest/70 p-3.5"
                      >
                        <div class="flex items-start justify-between gap-3">
                          <div class="flex items-center gap-2.5">
                            <div class="w-8 h-8 rounded-lg bg-primary/5 text-primary flex items-center justify-center shrink-0">
                              <span class="material-symbols-outlined text-[18px]">{{ factor.icon }}</span>
                            </div>
                            <div>
                              <p class="text-[11px] text-on-surface-variant m-0">{{ factor.label }}</p>
                              <p class="text-base font-bold text-on-surface m-0 mt-1 tabular-nums">{{ formatAttendanceValue(factor) }}</p>
                            </div>
                          </div>
                          <span class="inline-flex rounded-full border px-2 py-1 text-[9px] font-semibold whitespace-nowrap" :class="attendanceFactorStatus(factor).className">
                            {{ attendanceFactorStatus(factor).label }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="rounded-lg border border-orange-200 bg-orange-50/70 px-4 py-3 text-xs text-orange-800 payroll-notice">
                    薪资金额来自薪资记录，影响因素来自所选月份的数据库考勤汇总；最终薪资结果以薪酬审核记录为准。
                  </div>
                  <p class="text-[10px] text-on-surface-variant m-0 mt-3">数据来源：本人薪资记录与月度考勤汇总数据库接口 · 查询时间：{{ turn.completedAt }}</p>
                </template>

                <!-- Policy result -->
                <template v-else-if="turn.intent === 'POLICY' && turn.policyResult">
                  <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-5">
                    <div>
                      <h3 class="text-lg font-bold text-on-surface m-0">政策数据库查询结果</h3>
                      <p class="text-xs text-on-surface-variant m-0 mt-1.5">检索关键词：{{ turn.policyResult.searchKeywords.join('、') || '政策' }}</p>
                    </div>
                    <span class="self-start inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-[11px] font-semibold text-primary">
                      {{ turn.policyResult.documents.length }} 篇文档
                    </span>
                  </div>

                  <div v-if="turn.policyResult.documents.length === 0" class="rounded-xl border border-dashed border-outline-variant bg-surface-container-low/30 p-6 text-center">
                    <span class="material-symbols-outlined text-[30px] text-outline">find_in_page</span>
                    <p class="text-sm font-semibold text-on-surface m-0 mt-2">数据库中没有匹配的政策记录</p>
                    <p class="text-xs text-on-surface-variant m-0 mt-1.5">可尝试使用政策标题、分类或文档编号中的关键词重新查询。</p>
                  </div>

                  <div v-else class="space-y-3">
                    <article
                      v-for="document in turn.policyResult.documents"
                      :key="document.id"
                      class="rounded-xl border border-outline-variant/40 bg-surface-container-low/40 p-4 transition-colors hover:border-primary/40"
                    >
                      <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                        <div class="min-w-0">
                          <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-primary text-[19px]">policy</span>
                            <h4 class="text-sm font-bold text-on-surface m-0 break-words">{{ document.title }}</h4>
                          </div>
                          <div class="flex flex-wrap gap-2 mt-2">
                            <span class="rounded-full bg-primary/5 border border-primary/15 px-2.5 py-1 text-[10px] font-medium text-primary">{{ document.category || '未分类' }}</span>
                            <span class="rounded-full bg-surface-container-lowest border border-outline-variant/40 px-2.5 py-1 text-[10px] text-on-surface-variant">版本 {{ document.version || '—' }}</span>
                            <span class="rounded-full bg-surface-container-lowest border border-outline-variant/40 px-2.5 py-1 text-[10px] text-on-surface-variant">更新于 {{ formatDate(document.updated_at) }}</span>
                          </div>
                        </div>
                      </div>

                      <p class="text-sm text-on-surface-variant m-0 mt-3 leading-relaxed whitespace-pre-wrap">{{ policySummary(document) }}</p>
                      <div class="flex flex-wrap items-center gap-2 mt-3">
                        <span class="text-[10px] text-on-surface-variant">匹配关键词</span>
                        <span
                          v-for="keyword in matchedPolicyKeywords(document, turn.policyResult.searchKeywords)"
                          :key="`${document.id}-${keyword}`"
                          class="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[9px] font-semibold text-emerald-700 policy-match-badge"
                        >{{ keyword }}</span>
                        <span v-if="matchedPolicyKeywords(document, turn.policyResult.searchKeywords).length === 0" class="text-[10px] text-outline">—</span>
                      </div>

                      <button
                        type="button"
                        class="mt-4 w-full flex items-center justify-between px-3 py-2 bg-surface-container-lowest hover:bg-primary/5 border border-outline-variant/40 hover:border-primary/40 rounded-lg transition-colors text-primary text-[13px] font-medium"
                        @click="openPolicyDetail(document)"
                      >
                        <span>查看完整政策</span>
                        <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                      </button>
                    </article>
                  </div>

                  <p class="text-[10px] text-on-surface-variant m-0 mt-4">数据来源：政策中心数据库接口 · 查询时间：{{ turn.completedAt }}</p>
                </template>

                <!-- Unknown intent never calls a business API. -->
                <template v-else>
                  <div class="flex items-start gap-3 mb-4">
                    <span class="material-symbols-outlined text-primary text-[22px]">info</span>
                    <div>
                      <p class="text-sm font-semibold text-on-surface m-0">{{ turn.assistantReply || '暂时无法识别这个查询意图' }}</p>
                      <p class="text-xs text-on-surface-variant m-0 mt-1.5">本回合未调用业务接口。目前支持查询：</p>
                    </div>
                  </div>
                  <ol class="list-decimal pl-5 text-sm text-on-surface space-y-2 m-0">
                    <li>剩余假期和假期余额</li>
                    <li>本人薪资及考勤影响因素</li>
                    <li>公司政策、制度和员工手册</li>
                  </ol>
                </template>
              </div>
            </div>
          </template>
        </div>

        <!-- Input Area -->
        <div class="p-5 border-t border-outline-variant/40 bg-surface-container-lowest/80 backdrop-blur-xl z-20">
          <div class="flex gap-2 overflow-x-auto no-scrollbar pb-3 mb-2">
            <button
              type="button"
              class="whitespace-nowrap px-4 py-2 rounded-xl border border-outline-variant/60 bg-surface-container-lowest/50 text-on-surface text-sm hover:border-primary/50 hover:bg-primary/5 hover:text-primary transition-all flex items-center gap-2 shadow-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="queryActive"
              @click="submitAssistantQuery('请查询我当前年度的剩余假期。')"
            >
              <span class="material-symbols-outlined text-[18px] text-primary/70">beach_access</span>
              剩余假期查询
            </button>
            <button
              type="button"
              class="whitespace-nowrap px-4 py-2 rounded-xl border border-outline-variant/60 bg-surface-container-lowest/50 text-on-surface text-sm hover:border-primary/50 hover:bg-primary/5 hover:text-primary transition-all flex items-center gap-2 shadow-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="queryActive"
              @click="submitAssistantQuery('请查询我本月的薪资和可能影响薪资的考勤因素。')"
            >
              <span class="material-symbols-outlined text-[18px] text-emerald-600/70">payments</span>
              查看最新工资单
            </button>
          </div>

          <div class="relative group">
            <div class="absolute -inset-0.5 bg-gradient-to-r from-primary/30 to-tertiary/30 rounded-2xl blur opacity-30 group-hover:opacity-60 transition duration-500" />
            <div class="relative flex items-center bg-surface-container-lowest border border-outline-variant/50 rounded-2xl shadow-inner overflow-hidden focus-within:ring-1 focus-within:ring-primary focus-within:border-primary transition-all">
              <div class="pl-4 pr-2 flex items-center text-primary">
                <span class="material-symbols-outlined text-[24px]">auto_awesome</span>
              </div>
              <input
                v-model="assistantInput"
                type="text"
                maxlength="4000"
                placeholder="例如：查看上个月的薪资影响因素"
                class="w-full h-14 bg-transparent border-none focus:ring-0 text-sm text-on-surface placeholder:text-outline/60 px-2 outline-none disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="queryActive"
                @keydown.enter.prevent="submitInputQuery"
              />
              <div class="pr-2 flex gap-1">
                <button
                  type="button"
                  class="w-10 h-10 rounded-xl flex items-center justify-center text-outline opacity-50 cursor-not-allowed"
                  disabled
                  title="语音输入暂未开放"
                >
                  <span class="material-symbols-outlined text-[20px]">mic</span>
                </button>
                <button
                  type="button"
                  class="w-12 h-10 rounded-xl bg-gradient-to-r from-primary to-primary-container text-white flex items-center justify-center hover:shadow-lg hover:shadow-primary/30 transition-all ml-1 disabled:cursor-not-allowed disabled:opacity-50"
                  :disabled="queryActive || assistantInput.trim().length === 0"
                  @click="submitInputQuery"
                >
                  <span class="material-symbols-outlined text-[20px]">send</span>
                </button>
              </div>
            </div>
          </div>
          <div class="text-center mt-3">
            <span class="text-[10px] text-outline/70 font-medium">业务数据来自现有数据库接口，请以最终审核记录为准。</span>
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
            {{ dashboardInsight }}
          </p>
          <button
            type="button"
            class="mt-4 w-full py-2 px-4 bg-surface-container-lowest border border-primary/30 rounded-lg text-primary text-xs font-semibold hover:bg-primary/5 transition-colors flex items-center justify-center gap-2 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="queryActive"
            @click="submitAssistantQuery('请查询我当前年度的剩余假期。')"
          >
            <span class="material-symbols-outlined text-[16px]">search</span>
            查询我的假期
          </button>
        </div>

        <div class="bg-surface-container-lowest/80 rounded-2xl border border-outline-variant/40 shadow-lg p-5 glass-card">
          <h3 class="text-base font-semibold text-on-surface m-0 mb-5 flex items-center gap-2">
            <span class="material-symbols-outlined text-outline text-[20px]">dashboard</span>
            我的仪表板
          </h3>

          <div>
            <div class="flex justify-between items-end mb-2">
              <div>
                <span class="text-[10px] text-outline uppercase tracking-wider font-bold block mb-1">剩余年假</span>
                <div class="flex items-baseline gap-1">
                  <span class="text-3xl font-bold text-on-surface leading-none">{{ dashboardAnnualRemaining }}</span>
                  <span class="text-xs text-on-surface-variant font-medium">/ {{ dashboardAnnualTotal }} 天</span>
                </div>
              </div>
              <div class="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center text-primary-container">
                <span class="material-symbols-outlined text-[20px]">flight_takeoff</span>
              </div>
            </div>
            <div class="w-full bg-surface-variant h-2 rounded-full mt-3 overflow-hidden">
              <div class="bg-gradient-to-r from-primary to-tertiary h-full rounded-full" :style="{ width: `${dashboardAnnualRemainingRate}%` }" />
            </div>
            <p class="text-[10px] text-on-surface-variant m-0 mt-2">{{ dashboardStatusText }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Teleport avoids clipping and stacking contexts from the assistant/layout containers. -->
    <Teleport to="body">
      <div
        v-if="selectedPolicy"
        class="fixed inset-0 z-[9999] flex items-start sm:items-center justify-center overflow-y-auto bg-black/50 p-4 sm:p-6 backdrop-blur-sm"
        @click.self="closePolicyDetail"
      >
        <div
          ref="policyDialogRef"
          class="my-auto w-full max-w-2xl max-h-[calc(100vh-2rem)] sm:max-h-[85vh] overflow-y-auto rounded-2xl border border-outline-variant/50 bg-surface-container-lowest shadow-2xl outline-none"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="`policy-dialog-title-${selectedPolicy.id}`"
          tabindex="-1"
        >
          <div class="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-outline-variant/40 bg-surface-container-lowest/95 px-6 py-5 backdrop-blur-md">
            <div class="min-w-0">
              <p class="text-[10px] font-bold uppercase tracking-wider text-primary m-0">政策详情</p>
              <h3 :id="`policy-dialog-title-${selectedPolicy.id}`" class="text-lg font-bold text-on-surface m-0 mt-1 break-words">{{ selectedPolicy.title }}</h3>
            </div>
            <button
              type="button"
              class="w-9 h-9 rounded-lg border border-outline-variant/50 text-on-surface-variant hover:bg-surface-container-low flex items-center justify-center shrink-0"
              aria-label="关闭政策详情"
              @click="closePolicyDetail"
            >
              <span class="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>

          <div class="p-6">
            <dl class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
              <div class="rounded-xl border border-outline-variant/40 bg-surface-container-low/40 p-3">
                <dt class="text-[10px] text-on-surface-variant">文档编号</dt>
                <dd class="text-sm font-semibold text-on-surface m-0 mt-1 break-words">{{ selectedPolicy.document_code || '—' }}</dd>
              </div>
              <div class="rounded-xl border border-outline-variant/40 bg-surface-container-low/40 p-3">
                <dt class="text-[10px] text-on-surface-variant">分类</dt>
                <dd class="text-sm font-semibold text-on-surface m-0 mt-1">{{ selectedPolicy.category || '未分类' }}</dd>
              </div>
              <div class="rounded-xl border border-outline-variant/40 bg-surface-container-low/40 p-3">
                <dt class="text-[10px] text-on-surface-variant">版本</dt>
                <dd class="text-sm font-semibold text-on-surface m-0 mt-1">{{ selectedPolicy.version || '—' }}</dd>
              </div>
              <div class="rounded-xl border border-outline-variant/40 bg-surface-container-low/40 p-3">
                <dt class="text-[10px] text-on-surface-variant">更新时间</dt>
                <dd class="text-sm font-semibold text-on-surface m-0 mt-1">{{ formatDateTime(selectedPolicy.updated_at) }}</dd>
              </div>
            </dl>

            <section class="mb-5">
              <h4 class="text-sm font-bold text-on-surface m-0 mb-2">政策摘要</h4>
              <p class="rounded-xl border border-primary/15 bg-primary/5 p-4 text-sm text-on-surface-variant m-0 leading-relaxed whitespace-pre-wrap">{{ policySummary(selectedPolicy) }}</p>
            </section>

            <section v-if="safePolicyMetadata(selectedPolicy).length > 0" class="mb-5">
              <h4 class="text-sm font-bold text-on-surface m-0 mb-2">数据库详情</h4>
              <dl class="divide-y divide-outline-variant/30 rounded-xl border border-outline-variant/40 bg-surface-container-low/20 px-4">
                <div v-for="item in safePolicyMetadata(selectedPolicy)" :key="item.key" class="grid grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)] gap-4 py-3">
                  <dt class="text-xs text-on-surface-variant break-words">{{ item.label }}</dt>
                  <dd class="text-xs font-medium text-on-surface m-0 break-words whitespace-pre-wrap">{{ item.value }}</dd>
                </div>
              </dl>
            </section>

            <div class="rounded-xl border border-outline-variant/40 bg-surface-container-low/40 p-4">
              <p class="text-xs text-on-surface-variant m-0 leading-relaxed">数据库当前保存的是政策摘要和文档来源，完整正文请通过政策原文入口查看。</p>
              <a
                v-if="policySourceHref(selectedPolicy.source_path)"
                :href="policySourceHref(selectedPolicy.source_path) || undefined"
                target="_blank"
                rel="noopener noreferrer"
                class="mt-3 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-white hover:shadow-lg hover:shadow-primary/20 transition-shadow"
              >
                打开政策原文
                <span class="material-symbols-outlined text-[16px]">open_in_new</span>
              </a>
              <p v-else class="text-xs text-outline m-0 mt-3">数据库当前未提供可直接打开的政策原文来源。</p>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { ApiClientError } from '../shared/api/apiClient';
import { fetchMonthlyAttendanceSummary } from '../shared/api/modules/attendance';
import { fetchLeaveOverview, type LeaveBalanceItem } from '../shared/api/modules/employee';
import { fetchMySalary, type SalaryDetail } from '../shared/api/modules/payroll';
import { fetchPolicies, type PolicyDocument } from '../shared/api/modules/policy';
import {
  sendAssistantChat,
  type AssistantChatMessage,
  type AssistantChatResponse,
  type AssistantIntent,
  type AssistantResolvedParameters,
} from '../shared/api/modules/assistant';

type AssistantTurnStatus = 'loading' | 'success' | 'error';
type DashboardStatus = 'loading' | 'success' | 'empty' | 'error';
type BusinessIntent = Exclude<AssistantIntent, 'CHAT' | 'UNKNOWN'>;
type UnderstandingMode = 'MODEL' | 'LOCAL_FALLBACK';

interface PayrollPeriod {
  year: number;
  month: number;
  label: string;
}

interface MonthlyAttendanceSummary {
  late_count: number | null;
  early_leave_count: number | null;
  absent_count: number | null;
  unpaid_leave_count: number | null;
  approved_annual_leave_count: number | null;
  normal_count: number | null;
}

interface AttendanceFactor {
  key: keyof MonthlyAttendanceSummary;
  label: string;
  value: number | null;
  unit: string;
  icon: string;
  riskWhenPositive: boolean;
}

interface LeaveResult {
  year: number;
  balances: LeaveBalanceItem[];
}

interface PayrollResult {
  salary: SalaryDetail;
  attendance: MonthlyAttendanceSummary;
  period: PayrollPeriod;
}

interface PolicyResult {
  documents: PolicyDocument[];
  searchKeywords: string[];
}

interface AssistantTurn {
  id: string;
  prompt: string;
  keywords: string[];
  intent: AssistantIntent;
  status: AssistantTurnStatus;
  logs: string[];
  visibleLogCount: number;
  logAnimationActive: boolean;
  logsComplete: boolean;
  progressComplete: boolean;
  requestComplete: boolean;
  completedAt?: string;
  errorMessage?: string;
  assistantReply?: string;
  normalizedQuery?: string;
  resolvedParameters?: AssistantResolvedParameters;
  understandingMode?: UnderstandingMode;
  leaveResult?: LeaveResult;
  payrollResult?: PayrollResult;
  policyResult?: PolicyResult;
}

interface SafeMetadataItem {
  key: string;
  label: string;
  value: string;
}

const LEAVE_KEYWORDS = [
  '剩余假期', '假期余额', '休假余额', '还有多少假', '请假记录', '假期', '年假', '病假', '调休', '休假',
] as const;
const PAYROLL_KEYWORDS = [
  '基本工资', '工资单', '无薪假', '工资', '薪资', '月薪', '收入', '薪酬', '扣款', '实发', '缺勤', '迟到', '早退',
] as const;
const POLICY_PRIORITY_KEYWORDS = [
  '员工手册', '公司规定', '报销规定', '考勤制度', '薪资制度', '休假政策', '假期结转', '结转规定', '政策', '制度', '规定', '结转',
] as const;
const ALL_KEYWORDS = Array.from(new Set<string>([
  ...POLICY_PRIORITY_KEYWORDS,
  ...PAYROLL_KEYWORDS,
  ...LEAVE_KEYWORDS,
]));
const POLICY_SEARCH_TERMS = [
  '员工手册', '公司规定', '报销', '考勤', '薪资', '休假', '年假', '病假', '调休', '结转', '假期', '政策', '制度', '规定',
] as const;
const GENERIC_POLICY_TERMS = new Set(['公司规定', '政策', '制度', '规定']);
const leaveTypeOrder: Record<string, number> = { ANNUAL: 0, SICK: 1, COMP_TIME: 2 };
const MAX_RECENT_CONTEXT_MESSAGES = 12;
const MAX_CONTEXT_MESSAGE_LENGTH = 1_000;
const MAX_CONVERSATION_SUMMARY_LENGTH = 4_000;
const MODEL_UNAVAILABLE_REPLY = '智能对话模型当前不可用，但您仍可查询本人假期、薪资与考勤影响因素，以及公司政策。';

const chatHistoryRef = ref<HTMLElement | null>(null);
const policyDialogRef = ref<HTMLDivElement | null>(null);
const assistantInput = ref('');
const turns = ref<AssistantTurn[]>([]);
const conversationSummary = ref('');
const recentContextMessages = ref<AssistantChatMessage[]>([]);
const lastBusinessIntent = ref<BusinessIntent | null>(null);
const selectedPolicy = ref<PolicyDocument | null>(null);
const conversationStartedAt = new Date();
const dashboardBalances = ref<LeaveBalanceItem[]>([]);
const dashboardStatus = ref<DashboardStatus>('loading');
let turnSequence = 0;
let bodyOverflowBeforeDialog: string | null = null;

const queryActive = computed(() => turns.value.some((turn) => !canShowResult(turn)));
const conversationTimeLabel = formatConversationTime(conversationStartedAt);
const dashboardAnnualBalance = computed(() => dashboardBalances.value.find((balance) => balance.leave_type === 'ANNUAL'));
const dashboardAnnualRemaining = computed(() => {
  const balance = dashboardAnnualBalance.value;
  return balance ? formatLeaveAmount(remainingLeave(balance)) : '—';
});
const dashboardAnnualTotal = computed(() => {
  const balance = dashboardAnnualBalance.value;
  return balance ? formatLeaveAmount(balance.total_days) : '—';
});
const dashboardAnnualRemainingRate = computed(() => {
  const balance = dashboardAnnualBalance.value;
  if (!balance || Number(balance.total_days) <= 0) return 0;
  return Math.min(100, Math.max(0, Math.round(remainingLeave(balance) * 100 / Number(balance.total_days))));
});
const dashboardStatusText = computed(() => {
  if (dashboardStatus.value === 'loading') return '正在加载数据库假期账户…';
  if (dashboardStatus.value === 'error') return '当前无法读取假期账户。';
  if (dashboardStatus.value === 'empty' || !dashboardAnnualBalance.value) return '数据库当前没有可展示的年假账户。';
  return `数据年度：${dashboardAnnualBalance.value.year}`;
});
const dashboardInsight = computed(() => {
  if (dashboardStatus.value === 'loading') return '正在从员工假期账户加载可展示信息。';
  if (dashboardStatus.value === 'error') return '当前无法读取假期账户，您仍可稍后通过智能助手重新查询。';
  const balance = dashboardAnnualBalance.value;
  if (!balance) return '数据库当前没有可展示的年假账户信息。';
  return `${balance.year} 年年假账户当前剩余 ${formatLeaveAmount(remainingLeave(balance))} 天，已使用 ${formatLeaveAmount(balance.used_days)} 天，总额度 ${formatLeaveAmount(balance.total_days)} 天。`;
});

const vAutoScroll = {
  mounted(element: HTMLElement) {
    element.scrollTop = element.scrollHeight;
  },
  updated(element: HTMLElement) {
    element.scrollTop = element.scrollHeight;
  },
};

function extractKeywords(input: string): string[] {
  const normalizedInput = input.trim().toLowerCase();
  return ALL_KEYWORDS
    .map((keyword) => ({ keyword, index: normalizedInput.indexOf(keyword.toLowerCase()) }))
    .filter((match) => match.index >= 0)
    .sort((left, right) => left.index - right.index || right.keyword.length - left.keyword.length)
    .map((match) => match.keyword);
}

function classifyIntent(input: string, keywords: string[]): AssistantIntent {
  const normalizedInput = input.trim().toLowerCase();
  const containsTerm = (terms: readonly string[]) => terms.some((term) => normalizedInput.includes(term.toLowerCase()));
  if (containsTerm(POLICY_PRIORITY_KEYWORDS)) return 'POLICY';
  if (containsTerm(PAYROLL_KEYWORDS) || keywords.some((keyword) => PAYROLL_KEYWORDS.includes(keyword as typeof PAYROLL_KEYWORDS[number]))) return 'PAYROLL';
  if (containsTerm(LEAVE_KEYWORDS) || keywords.some((keyword) => LEAVE_KEYWORDS.includes(keyword as typeof LEAVE_KEYWORDS[number]))) return 'LEAVE';
  return 'UNKNOWN';
}

function extractPolicySearchKeywords(input: string): string[] {
  const normalizedInput = input.trim().toLowerCase();
  const terms = POLICY_SEARCH_TERMS.filter((term) => normalizedInput.includes(term.toLowerCase()));
  return Array.from(new Set<string>(terms)).slice(0, 3);
}

function parsePayrollPeriod(input: string, now = new Date()): PayrollPeriod {
  const explicitPeriod = input.match(/(\d{4})\s*年\s*(\d{1,2})\s*月/);
  if (explicitPeriod) {
    const year = Number(explicitPeriod[1]);
    const month = Number(explicitPeriod[2]);
    if (year >= 2000 && year <= 2100 && month >= 1 && month <= 12) {
      return { year, month, label: `${year} 年 ${month} 月` };
    }
  }

  if (input.includes('上个月') || input.includes('上月')) {
    const previousMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    return {
      year: previousMonth.getFullYear(),
      month: previousMonth.getMonth() + 1,
      label: `${previousMonth.getFullYear()} 年 ${previousMonth.getMonth() + 1} 月`,
    };
  }

  return {
    year: now.getFullYear(),
    month: now.getMonth() + 1,
    label: `${now.getFullYear()} 年 ${now.getMonth() + 1} 月`,
  };
}

function parseLeaveYear(input: string, now = new Date()): number {
  const explicitYear = input.match(/(\d{4})\s*年/);
  const year = explicitYear ? Number(explicitYear[1]) : now.getFullYear();
  return year >= 2000 && year <= 2100 ? year : now.getFullYear();
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function nullableNumber(value: unknown): number | null {
  if (typeof value !== 'number' && typeof value !== 'string') return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function normalizeAttendanceSummary(value: unknown): MonthlyAttendanceSummary {
  const record = isRecord(value) ? value : {};
  return {
    late_count: nullableNumber(record.late_count),
    early_leave_count: nullableNumber(record.early_leave_count),
    absent_count: nullableNumber(record.absent_count),
    unpaid_leave_count: nullableNumber(record.unpaid_leave_count),
    approved_annual_leave_count: nullableNumber(record.approved_annual_leave_count),
    normal_count: nullableNumber(record.normal_count),
  };
}

function canShowResult(turn: AssistantTurn): boolean {
  return turn.requestComplete && turn.progressComplete && turn.logsComplete;
}

function turnStatusLabel(turn: AssistantTurn): string {
  if (!turn.requestComplete) return '正在查询';
  if (!turn.progressComplete || !turn.logsComplete) return turn.status === 'error' ? '正在整理错误信息' : '正在整理';
  return turn.status === 'error' ? '查询失败' : '查询完成';
}

function intentLabel(intent: AssistantIntent): string {
  return { LEAVE: '假期', PAYROLL: '薪资', POLICY: '政策', CHAT: '普通对话', UNKNOWN: '能力范围' }[intent];
}

function formatConversationTime(date: Date): string {
  return `今天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })}`;
}

function formatQueryTime(date: Date): string {
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

function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

function safeErrorMessage(error: unknown): string {
  if (!(error instanceof ApiClientError)) return '请求未能完成，请稍后重试。';
  if (error.status === 401) return '登录状态已失效，请重新登录。';
  if (error.status === 403) return '当前账号无权查看该数据。';
  if (error.status === 404) return '数据库中没有对应记录。';
  if (error.status !== undefined && error.status >= 500) return '服务暂时不可用，请稍后重试。';
  if (error.status !== undefined && error.status >= 400) return '请求参数或当前数据状态不满足查询条件。';
  return '网络连接失败或服务端未响应，请稍后重试。';
}

function isErrorLog(log: string): boolean {
  return log.includes('失败') || log.includes('错误');
}

async function scrollChatToLatest(): Promise<void> {
  await nextTick();
  const chatHistory = chatHistoryRef.value;
  if (!chatHistory) return;
  chatHistory.scrollTo({ top: chatHistory.scrollHeight, behavior: 'smooth' });
}

function revealNextLog(turn: AssistantTurn): void {
  if (turn.logAnimationActive) return;
  if (turn.visibleLogCount < turn.logs.length) {
    turn.visibleLogCount += 1;
    turn.logAnimationActive = true;
    void scrollChatToLatest();
    return;
  }
  if (turn.requestComplete) {
    turn.logsComplete = true;
    void scrollChatToLatest();
  }
}

function notifyLogsChanged(turn: AssistantTurn): void {
  revealNextLog(turn);
  void scrollChatToLatest();
}

function handleLogAnimationEnd(turn: AssistantTurn, logIndex: number): void {
  if (logIndex !== turn.visibleLogCount - 1) return;
  turn.logAnimationActive = false;
  revealNextLog(turn);
}

function markProgressComplete(turn: AssistantTurn): void {
  turn.progressComplete = true;
  void scrollChatToLatest();
}

function createTurn(prompt: string): AssistantTurn {
  const keywords = extractKeywords(prompt);
  turnSequence += 1;
  return reactive<AssistantTurn>({
    id: `assistant-turn-${turnSequence}`,
    prompt,
    keywords,
    intent: 'UNKNOWN',
    status: 'loading',
    logs: [
      '[问题理解] 正在结合会话摘要和最近消息理解当前问题',
    ],
    visibleLogCount: 1,
    logAnimationActive: true,
    logsComplete: false,
    progressComplete: false,
    requestComplete: false,
  });
}

async function executeLeaveQuery(turn: AssistantTurn): Promise<void> {
  const year = turn.resolvedParameters?.year ?? parseLeaveYear(turn.prompt);
  turn.logs.push('[身份上下文] 使用当前登录用户关联员工档案');
  turn.logs.push(`[接口请求] 调用 /employees/me/leave-overview?year=${year}`);
  notifyLogsChanged(turn);

  const overview = await fetchLeaveOverview(year);
  const balances = [...overview.balances].sort(
    (left, right) => (leaveTypeOrder[left.leave_type] ?? Number.MAX_SAFE_INTEGER) - (leaveTypeOrder[right.leave_type] ?? Number.MAX_SAFE_INTEGER),
  );
  turn.leaveResult = { year, balances };
  turn.logs.push(`[数据返回] 已获取 ${balances.length} 条假期余额记录`);
  turn.logs.push(balances.length > 0 ? '[结果整理] 已生成假期统计卡片、进度与余额表格' : '[结果整理] 已生成假期余额空状态');
  dashboardBalances.value = balances;
  dashboardStatus.value = balances.length > 0 ? 'success' : 'empty';
  notifyLogsChanged(turn);
}

async function executePayrollQuery(turn: AssistantTurn): Promise<void> {
  const parsedPeriod = parsePayrollPeriod(turn.prompt);
  const year = turn.resolvedParameters?.year ?? parsedPeriod.year;
  const month = turn.resolvedParameters?.month ?? parsedPeriod.month;
  const period: PayrollPeriod = { year, month, label: `${year} 年 ${month} 月` };
  turn.logs.push('[身份上下文] 使用当前登录用户关联员工档案');
  turn.logs.push('[接口请求] 调用 /payroll/me');
  notifyLogsChanged(turn);

  const salary = await fetchMySalary();
  turn.logs.push('[数据返回] 已获取本人薪资主记录');
  turn.logs.push(`[接口请求] 调用 /attendance/monthly?year=${period.year}&month=${period.month}`);
  notifyLogsChanged(turn);

  const rawAttendance: unknown = await fetchMonthlyAttendanceSummary(period.year, period.month, salary.employee_id);
  const attendance = normalizeAttendanceSummary(rawAttendance);
  turn.payrollResult = { salary, attendance, period };
  turn.logs.push(`[数据返回] 已获取 ${period.label}数据库考勤汇总`);
  turn.logs.push('[结果整理] 已生成薪资记录与考勤影响因素视图');
  notifyLogsChanged(turn);
}

function policySearchText(document: PolicyDocument): string {
  const summary = typeof document.metadata_json.summary === 'string' ? document.metadata_json.summary : '';
  return [document.title, document.category, document.document_code, summary].join('\n').toLowerCase();
}

function filterPolicyDocuments(documents: PolicyDocument[], keywords: string[]): PolicyDocument[] {
  if (keywords.length === 0) return documents;
  const specificKeywords = keywords.filter((keyword) => !GENERIC_POLICY_TERMS.has(keyword));
  const matchTerms = specificKeywords.length > 0 ? specificKeywords : keywords;
  return documents.filter((document) => {
    const searchText = policySearchText(document);
    return matchTerms.some((keyword) => searchText.includes(keyword.toLowerCase()));
  });
}

async function executePolicyQuery(turn: AssistantTurn): Promise<void> {
  const searchKeywords = turn.resolvedParameters?.policy_keywords.length
    ? turn.resolvedParameters.policy_keywords
    : extractPolicySearchKeywords(turn.prompt);
  turn.logs.push('[接口请求] 正在检索政策中心数据库');
  if (searchKeywords.length > 0) {
    searchKeywords.forEach((keyword) => turn.logs.push(`[接口请求] 调用 /policies?query=${keyword}`));
  }
  notifyLogsChanged(turn);

  const overviews = searchKeywords.length > 0
    ? await Promise.all(searchKeywords.map((keyword) => fetchPolicies(keyword)))
    : [];
  const mergedById = new Map<number, PolicyDocument>();
  overviews.forEach((overview) => overview.documents.forEach((document) => mergedById.set(document.id, document)));

  if (mergedById.size === 0) {
    turn.logs.push('[接口请求] 关键词查询无结果，调用 /policies 获取全部数据库政策');
    notifyLogsChanged(turn);
    const allPolicies = await fetchPolicies();
    allPolicies.documents.forEach((document) => mergedById.set(document.id, document));
  }

  const documents = filterPolicyDocuments(Array.from(mergedById.values()), searchKeywords)
    .sort((left, right) => new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime());
  turn.policyResult = { documents, searchKeywords };
  turn.logs.push(`[数据返回] 已匹配 ${documents.length} 篇政策文档`);
  turn.logs.push(documents.length > 0 ? '[结果整理] 已生成政策摘要与来源信息' : '[结果整理] 已生成政策查询空状态');
  notifyLogsChanged(turn);
}

function executeUnknownQuery(turn: AssistantTurn): void {
  turn.logs.push('[数据查询] 未识别为支持的业务查询，未调用业务接口');
  turn.logs.push('[结果整理] 已生成当前能力范围提示');
  notifyLogsChanged(turn);
}

function executeChatReply(turn: AssistantTurn): void {
  turn.logs.push('[结果整理] 已生成安全文本回复');
  notifyLogsChanged(turn);
}

async function dispatchTurn(turn: AssistantTurn): Promise<void> {
  if (turn.intent === 'LEAVE') return executeLeaveQuery(turn);
  if (turn.intent === 'PAYROLL') return executePayrollQuery(turn);
  if (turn.intent === 'POLICY') return executePolicyQuery(turn);
  if (turn.intent === 'CHAT') return executeChatReply(turn);
  executeUnknownQuery(turn);
}

function isBusinessIntent(intent: AssistantIntent): intent is BusinessIntent {
  return intent === 'LEAVE' || intent === 'PAYROLL' || intent === 'POLICY';
}

function isExplicitFollowUp(prompt: string): boolean {
  const normalized = prompt.trim().replace(/[。！!]/g, '');
  if (normalized.length > 24) return false;
  return /(?:呢[？?]?$|^(?:那|那么|这个|这个月|上个月|上月)(?:.*)?[？?]?$|^继续(?:查|说|看)?[？?]?$)/.test(normalized);
}

function parameterLog(parameters: AssistantResolvedParameters): string | null {
  if (parameters.year && parameters.month) return `[参数解析] 已解析查询周期：${parameters.year} 年 ${parameters.month} 月`;
  if (parameters.year) return `[参数解析] 已解析查询年度：${parameters.year} 年`;
  if (parameters.policy_keywords.length > 0) return `[参数解析] 已提取政策关键词：${parameters.policy_keywords.join('、')}`;
  return null;
}

function applyAssistantResponse(turn: AssistantTurn, response: AssistantChatResponse): void {
  turn.intent = response.intent;
  turn.assistantReply = response.reply;
  turn.normalizedQuery = response.normalized_query;
  turn.resolvedParameters = response.parameters;
  turn.understandingMode = 'MODEL';
  conversationSummary.value = sanitizeContextText(
    response.updated_summary,
    MAX_CONVERSATION_SUMMARY_LENGTH,
  );
  turn.logs.push('[问题理解] 已结合会话摘要和最近消息理解当前问题');
  turn.logs.push(response.intent === 'CHAT'
    ? '[意图识别] 已识别为普通对话'
    : `[意图识别] 已识别查询类型：${response.intent}`);
  const resolvedParameterLog = parameterLog(response.parameters);
  if (resolvedParameterLog) turn.logs.push(resolvedParameterLog);
  notifyLogsChanged(turn);
}

async function resolveTurnUnderstanding(turn: AssistantTurn): Promise<void> {
  try {
    const response = await sendAssistantChat({
      message: turn.prompt,
      conversation_summary: conversationSummary.value,
      recent_messages: recentContextMessages.value.map((message) => ({ ...message })),
    });
    applyAssistantResponse(turn, response);
  } catch (error: unknown) {
    if (error instanceof ApiClientError && error.status !== undefined && error.status < 500) {
      throw error;
    }
    turn.understandingMode = 'LOCAL_FALLBACK';
    const localIntent = classifyIntent(turn.prompt, turn.keywords);
    turn.intent = isExplicitFollowUp(turn.prompt) && lastBusinessIntent.value
      ? lastBusinessIntent.value
      : localIntent;
    turn.assistantReply = turn.intent === 'UNKNOWN' ? MODEL_UNAVAILABLE_REPLY : undefined;
    turn.logs.push('[问题理解] 智能理解服务当前不可用');
    turn.logs.push(`[兼容兜底] 已使用本地关键词规则${turn.intent !== localIntent ? '并继承最近业务意图' : ''}`);
    turn.logs.push(`[意图识别] 本地识别查询类型：${turn.intent}`);
    notifyLogsChanged(turn);
  }
}

function sanitizeContextText(value: string, maxLength: number): string {
  return value
    .trim()
    .replace(/\bBearer\s+[A-Za-z0-9._~+/=-]+/gi, '[已脱敏凭证]')
    .replace(/(?:api[_ -]?key|token|密码|password|员工编号|employee[_ -]?id|用户\s*id|user[_ -]?id)\s*[:：=]?\s*[A-Za-z0-9._~+/=-]{3,}/gi, '[已脱敏敏感字段]')
    .replace(/(?:实发工资|基本工资|绩效工资|扣款|工资|薪资|金额)[^\n，。；]{0,12}\d+(?:\.\d+)?\s*(?:元|人民币|CNY|RMB)/gi, '[已脱敏薪资金额]')
    .slice(0, maxLength);
}

function assistantContextNote(turn: AssistantTurn, succeeded: boolean): string {
  if (turn.intent === 'CHAT') return turn.assistantReply || '已完成普通对话。';
  if (turn.intent === 'PAYROLL') {
    const period = turn.payrollResult?.period;
    const target = period ? `${period.year} 年 ${period.month} 月` : '所选月份';
    return `${succeeded ? '已完成' : '已识别'} PAYROLL 查询，查询周期为 ${target}，未向模型传递薪资金额。`;
  }
  if (turn.intent === 'LEAVE') {
    const year = turn.leaveResult?.year ?? turn.resolvedParameters?.year;
    return `${succeeded ? '已完成' : '已识别'} LEAVE 查询${year ? `，查询年度为 ${year} 年` : ''}，未向模型传递具体余额。`;
  }
  if (turn.intent === 'POLICY') {
    const keywords = turn.policyResult?.searchKeywords ?? turn.resolvedParameters?.policy_keywords ?? [];
    return `${succeeded ? '已完成' : '已识别'} POLICY 查询${keywords.length ? `，关键词为${keywords.join('、')}` : ''}，未保存政策正文。`;
  }
  return turn.assistantReply || '本轮问题未调用业务接口。';
}

function appendRecentContext(turn: AssistantTurn, succeeded: boolean): void {
  const userContent = sanitizeContextText(turn.prompt, MAX_CONTEXT_MESSAGE_LENGTH);
  const assistantContent = sanitizeContextText(
    assistantContextNote(turn, succeeded),
    MAX_CONTEXT_MESSAGE_LENGTH,
  );
  const nextMessages = [...recentContextMessages.value];
  if (userContent) nextMessages.push({ role: 'user', content: userContent });
  if (assistantContent) nextMessages.push({ role: 'assistant', content: assistantContent });
  recentContextMessages.value = nextMessages.slice(-MAX_RECENT_CONTEXT_MESSAGES);
}

async function submitAssistantQuery(prompt: string): Promise<void> {
  if (queryActive.value || prompt.trim().length === 0) return;
  const turn = createTurn(prompt);
  turns.value.push(turn);
  await scrollChatToLatest();

  let succeeded = false;
  try {
    await resolveTurnUnderstanding(turn);
    await dispatchTurn(turn);
    if (isBusinessIntent(turn.intent)) lastBusinessIntent.value = turn.intent;
    turn.status = 'success';
    succeeded = true;
  } catch (error: unknown) {
    const errorMessage = safeErrorMessage(error);
    turn.errorMessage = errorMessage;
    turn.logs.push(`[接口失败] ${intentLabel(turn.intent)}查询失败：${errorMessage}`);
    turn.logs.push('[结果整理] 已生成安全错误提示');
    turn.status = 'error';
  } finally {
    appendRecentContext(turn, succeeded);
    turn.completedAt = formatQueryTime(new Date());
    turn.requestComplete = true;
    assistantInput.value = '';
    notifyLogsChanged(turn);
  }
}

async function submitInputQuery(): Promise<void> {
  const prompt = assistantInput.value;
  await submitAssistantQuery(prompt);
}

function clearConversation(): void {
  if (queryActive.value) return;
  turns.value = [];
  conversationSummary.value = '';
  recentContextMessages.value = [];
  lastBusinessIntent.value = null;
  assistantInput.value = '';
  closePolicyDetail();
}

function leaveBalances(turn: AssistantTurn): LeaveBalanceItem[] {
  return turn.leaveResult?.balances ?? [];
}

function leaveResultYear(turn: AssistantTurn): number {
  return turn.leaveResult?.year ?? new Date().getFullYear();
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
  return { ANNUAL: 'flight_takeoff', SICK: 'medical_services', COMP_TIME: 'schedule' }[type] ?? 'event_available';
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
  return total > 0 ? Math.min(100, Math.max(0, Math.round(used * 100 / total))) : 0;
}

function leaveBalanceStatus(balance: LeaveBalanceItem): { label: string; className: string } {
  const total = Number(balance.total_days);
  const remaining = remainingLeave(balance);
  if (total <= 0) return { label: '暂无额度', className: 'leave-status--empty' };
  if (remaining <= 0) return { label: '已用完', className: 'leave-status--exhausted' };
  if (remaining / total <= 0.2) return { label: '即将用完', className: 'leave-status--low' };
  return { label: '余额充足', className: 'leave-status--sufficient' };
}

function formatSalaryAmount(value: number | null): string {
  if (value === null) return '当前权限下不可见';
  return Number.isFinite(Number(value))
    ? Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    : '—';
}

function attendanceFactors(summary: MonthlyAttendanceSummary): AttendanceFactor[] {
  return [
    { key: 'normal_count', label: '正常出勤', value: summary.normal_count, unit: '天', icon: 'check_circle', riskWhenPositive: false },
    { key: 'late_count', label: '迟到次数', value: summary.late_count, unit: '次', icon: 'schedule', riskWhenPositive: true },
    { key: 'early_leave_count', label: '早退次数', value: summary.early_leave_count, unit: '次', icon: 'logout', riskWhenPositive: true },
    { key: 'absent_count', label: '缺勤天数', value: summary.absent_count, unit: '天', icon: 'event_busy', riskWhenPositive: true },
    { key: 'unpaid_leave_count', label: '无薪假天数', value: summary.unpaid_leave_count, unit: '天', icon: 'money_off', riskWhenPositive: true },
    { key: 'approved_annual_leave_count', label: '已批准年假天数', value: summary.approved_annual_leave_count, unit: '天', icon: 'beach_access', riskWhenPositive: false },
  ];
}

function formatAttendanceValue(factor: AttendanceFactor): string {
  return factor.value === null ? '—' : `${factor.value.toLocaleString('zh-CN', { maximumFractionDigits: 2 })} ${factor.unit}`;
}

function attendanceFactorStatus(factor: AttendanceFactor): { label: string; className: string } {
  if (factor.value === null) return { label: '数据缺失', className: 'attendance-status--empty' };
  if (factor.riskWhenPositive && factor.value > 0) return { label: '可能影响薪资', className: 'attendance-status--warning' };
  if (factor.key === 'normal_count') return { label: factor.value > 0 ? '正常' : '无记录', className: 'attendance-status--normal' };
  if (factor.key === 'approved_annual_leave_count' && factor.value > 0) return { label: '已记录', className: 'attendance-status--info' };
  return { label: '无影响记录', className: 'attendance-status--normal' };
}

function payrollRiskCount(summary: MonthlyAttendanceSummary): number {
  return [summary.late_count, summary.early_leave_count, summary.absent_count, summary.unpaid_leave_count]
    .filter((value): value is number => value !== null && value > 0)
    .length;
}

function payrollRiskSummary(summary: MonthlyAttendanceSummary): string {
  const riskCount = payrollRiskCount(summary);
  return riskCount > 0 ? `${riskCount} 项因素需要关注` : '未发现需提醒的影响因素';
}

function policySummary(document: PolicyDocument): string {
  const summary = document.metadata_json.summary;
  return typeof summary === 'string' && summary.trim().length > 0 ? summary.trim() : '数据库当前未提供政策摘要。';
}

function matchedPolicyKeywords(document: PolicyDocument, keywords: string[]): string[] {
  const searchText = policySearchText(document);
  return keywords.filter((keyword) => searchText.includes(keyword.toLowerCase()));
}

function isSafeMetadataKey(key: string): boolean {
  return !/(token|password|secret|credential|authorization|api[_-]?key)/i.test(key);
}

function metadataLabel(key: string): string {
  const labels: Record<string, string> = {
    author: '作者',
    department: '发布部门',
    effective_date: '生效日期',
    status: '状态',
    language: '语言',
    scope: '适用范围',
  };
  return labels[key] ?? key.replace(/_/g, ' ');
}

function safePolicyMetadata(document: PolicyDocument): SafeMetadataItem[] {
  return Object.entries(document.metadata_json)
    .filter(([key, value]) => key !== 'summary' && isSafeMetadataKey(key) && ['string', 'number', 'boolean'].includes(typeof value))
    .map(([key, value]) => ({
      key,
      label: metadataLabel(key),
      value: typeof value === 'boolean' ? (value ? '是' : '否') : String(value),
    }));
}

function policySourceHref(sourcePath: string | null): string | null {
  const value = sourcePath?.trim();
  if (!value) return null;
  if (/^https?:\/\//i.test(value) || value.startsWith('/') || !/^[a-z][a-z\d+.-]*:/i.test(value)) return value;
  return null;
}

async function openPolicyDetail(policyDocument: PolicyDocument): Promise<void> {
  if (bodyOverflowBeforeDialog === null) {
    bodyOverflowBeforeDialog = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
  }
  selectedPolicy.value = policyDocument;
  await nextTick();
  policyDialogRef.value?.focus();
}

function closePolicyDetail(): void {
  selectedPolicy.value = null;
  if (bodyOverflowBeforeDialog !== null) {
    document.body.style.overflow = bodyOverflowBeforeDialog;
    bodyOverflowBeforeDialog = null;
  }
}

function handleGlobalKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape' && selectedPolicy.value) closePolicyDetail();
}

async function loadDashboardLeaveOverview(): Promise<void> {
  dashboardStatus.value = 'loading';
  try {
    const overview = await fetchLeaveOverview();
    dashboardBalances.value = overview.balances;
    dashboardStatus.value = overview.balances.length > 0 ? 'success' : 'empty';
  } catch {
    dashboardBalances.value = [];
    dashboardStatus.value = 'error';
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown);
  void loadDashboardLeaveOverview();
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleGlobalKeydown);
  if (bodyOverflowBeforeDialog !== null) {
    document.body.style.overflow = bodyOverflowBeforeDialog;
    bodyOverflowBeforeDialog = null;
  }
});
</script>

<style scoped>
/* 每张过程卡片按“节点停留发光 → 连接线”顺序播放一次，由 animationend 报告完成。 */
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

.leave-status--sufficient,
.attendance-status--normal {
  border-color: #bbf7d0;
  background: #f0fdf4;
  color: #15803d;
}

.leave-status--low,
.attendance-status--warning {
  border-color: #fed7aa;
  background: #fff7ed;
  color: #c2410c;
}

.leave-status--exhausted {
  border-color: #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}

.leave-status--empty,
.attendance-status--empty {
  border-color: #d1d5db;
  background: #f3f4f6;
  color: #6b7280;
}

.attendance-status--info {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
}

:global([data-theme="dark"]) .leave-query-success-badge,
:global([data-theme="dark"]) .policy-match-badge,
:global([data-theme="dark"]) .leave-status--sufficient,
:global([data-theme="dark"]) .attendance-status--normal {
  background-color: #052e16 !important;
  border-color: #166534 !important;
  color: #86efac !important;
}

:global([data-theme="dark"]) .leave-status--low,
:global([data-theme="dark"]) .attendance-status--warning,
:global([data-theme="dark"]) .payroll-notice {
  background-color: #431407 !important;
  border-color: #9a3412 !important;
  color: #fdba74 !important;
}

:global([data-theme="dark"]) .leave-status--exhausted {
  background-color: #450a0a !important;
  border-color: #991b1b !important;
  color: #fca5a5 !important;
}

:global([data-theme="dark"]) .leave-status--empty,
:global([data-theme="dark"]) .attendance-status--empty {
  background-color: #1f2937 !important;
  border-color: #4b5563 !important;
  color: #d1d5db !important;
}

:global([data-theme="dark"]) .attendance-status--info {
  background-color: #172554 !important;
  border-color: #1e40af !important;
  color: #93c5fd !important;
}
</style>
