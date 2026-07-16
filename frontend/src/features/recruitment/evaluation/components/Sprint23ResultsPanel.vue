<template>
  <div class="space-y-6">
    <!-- Header -->
    <h2 class="text-lg font-bold flex items-center gap-2 px-2 text-slate-800">
      <div class="w-1.5 h-6 bg-teal-500 rounded-full"></div>
      岗位匹配与 AI 分析报告
    </h2>

    <!-- Candidate List Reports (Collapsible) -->
    <div v-for="candidate in displayCandidates" :key="candidate.id" class="recruitment-hover-card bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
      <!-- Collapse Toggle Header -->
      <div 
        class="px-6 py-5 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors select-none"
        @click="toggleReport(candidate.id)"
      >
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-lg">
            {{ candidate.name.charAt(0) }}
          </div>
          <div>
            <span class="text-base font-bold text-slate-800">{{ candidate.name }}</span>
            <div class="text-sm font-medium text-slate-500 mt-0.5">
              综合分: <span class="text-indigo-600 font-black">{{ formatNum(candidate.score) }}分</span>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-6">
          <span 
            v-if="candidate.riskLevel === 'HIGH'" 
            class="px-3 py-1 bg-red-50 text-red-600 rounded-md text-xs font-bold border border-red-100"
          >
            高风险项
          </span>
          <span 
            v-else 
            class="px-3 py-1 bg-amber-50 text-amber-600 rounded-md text-xs font-bold border border-amber-100"
          >
            需人工复核
          </span>
          
          <div :class="['transform transition-transform duration-300 text-slate-400', expandedReportId === candidate.id ? 'rotate-180' : '']">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Expanded Content details -->
      <div 
        v-show="expandedReportId === candidate.id" 
        class="border-t border-slate-100 transition-all duration-300"
      >
        <div class="p-6 space-y-6 bg-slate-50/30">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Left: Quantitative Dimensions & Questions -->
            <div class="space-y-4">
              <div>
                <h3 class="text-xs font-bold text-slate-800 mb-3 border-l-4 border-blue-500 pl-2 uppercase tracking-wider">量化匹配维度</h3>
                <div class="grid grid-cols-2 gap-3.5">
                  <div class="bg-white p-3.5 rounded-xl border border-slate-200/60 shadow-sm">
                    <div class="text-[10px] text-slate-400 font-bold mb-0.5">经验匹配</div>
                    <div class="text-lg font-black text-slate-800">
                      {{ formatNum(candidate.radar.exp) }}<span class="text-xs font-medium text-slate-400 ml-0.5">分</span>
                    </div>
                  </div>
                  <div class="bg-white p-3.5 rounded-xl border border-slate-200/60 shadow-sm">
                    <div class="text-[10px] text-slate-400 font-bold mb-0.5">技能匹配</div>
                    <div class="text-lg font-black text-slate-800">
                      {{ formatNum(candidate.radar.skill) }}<span class="text-xs font-medium text-slate-400 ml-0.5">分</span>
                    </div>
                  </div>
                  <div class="bg-white p-3.5 rounded-xl border border-slate-200/60 shadow-sm">
                    <div class="text-[10px] text-slate-400 font-bold mb-0.5">教育背景</div>
                    <div class="text-lg font-black text-slate-800">
                      {{ formatNum(candidate.radar.edu) }}<span class="text-xs font-medium text-slate-400 ml-0.5">分</span>
                    </div>
                  </div>
                  <div class="bg-white p-3.5 rounded-xl border border-slate-200/60 shadow-sm">
                    <div class="text-[10px] text-slate-400 font-bold mb-0.5">风险维度</div>
                    <div class="text-lg font-black" :class="candidate.radar.risk > 50 ? 'text-amber-600' : 'text-slate-800'">
                      {{ formatNum(candidate.radar.risk) }}<span class="text-xs font-medium text-slate-400 ml-0.5">分</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Matched Skills -->
              <div>
                <h4 class="text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-wider">已匹配的技能 ({{ candidate.matchedSkills.length }})</h4>
                <div class="flex flex-wrap gap-1.5">
                  <span 
                    v-for="(skill, idx) in candidate.matchedSkills" 
                    :key="idx"
                    class="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-md text-[10px] font-bold"
                  >
                    {{ skill }}
                  </span>
                  <span v-if="candidate.matchedSkills.length === 0" class="text-xs text-slate-400 italic">暂无完全匹配的技能</span>
                </div>
              </div>

              <!-- Suggested Interview Questions -->
              <div v-if="candidate.suggestedQuestions.length > 0" class="bg-white border border-slate-200/60 rounded-xl p-4 shadow-sm">
                <h4 class="text-[10px] font-bold text-slate-500 mb-2.5 flex items-center gap-1.5 uppercase tracking-wider">
                  <svg class="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-12-12 9 9 0 0112 12z" />
                  </svg>
                  建议面试追问问题
                </h4>
                <ul class="list-decimal pl-4.5 space-y-2 text-xs text-slate-600 font-medium leading-relaxed">
                  <li v-for="(question, qIdx) in candidate.suggestedQuestions" :key="qIdx">
                    {{ question }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- Right: AI Review conclusions & Findings -->
            <div class="space-y-4">
              <div>
                <h3 class="text-xs font-bold text-slate-800 mb-3 border-l-4 border-amber-500 pl-2 uppercase tracking-wider">AI 风险审查发现</h3>
                
                <!-- Severity conclusion box -->
                <div class="bg-red-50/50 border border-red-100 rounded-xl p-3.5 mb-3.5">
                  <div class="flex items-start gap-2.5">
                    <div class="mt-0.5 flex-shrink-0">
                      <svg class="w-4.5 h-4.5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    </div>
                    <div>
                      <h4 class="text-xs font-bold text-red-800">审查结论</h4>
                      <p class="text-xs text-red-600 mt-0.5 leading-relaxed font-semibold">{{ candidate.decisionRisk }}</p>
                    </div>
                  </div>
                </div>

                <!-- Detailed findings checklist -->
                <div v-if="candidate.findings.length > 0" class="space-y-2.5 mb-3.5">
                  <div 
                    v-for="(finding, fIdx) in candidate.findings" 
                    :key="fIdx"
                    class="bg-white border border-slate-200/60 rounded-xl p-3 shadow-sm flex items-start gap-3"
                  >
                    <span 
                      :class="[
                        'px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-wider',
                        finding.severity === 'HIGH' ? 'bg-red-50 text-red-600 border border-red-100' :
                        finding.severity === 'MEDIUM' ? 'bg-amber-50 text-amber-600 border border-amber-100' :
                        'bg-blue-50 text-blue-600 border border-blue-100'
                      ]"
                    >
                      {{ finding.severity }}
                    </span>
                    <div class="min-w-0 flex-1 leading-relaxed">
                      <strong class="block text-xs font-bold text-slate-800">{{ finding.code }}</strong>
                      <p class="text-xs text-slate-500 mt-0.5 font-medium">{{ finding.summary }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Missing Skills -->
              <div>
                <h4 class="text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-wider">缺失的关键技能 ({{ candidate.missingSkills.length }})</h4>
                <div class="flex flex-wrap gap-1.5">
                  <span 
                    v-for="(skill, idx) in candidate.missingSkills" 
                    :key="idx" 
                    class="px-2 py-0.5 bg-red-50 text-red-600 border border-red-100 rounded-md text-[10px] font-bold"
                  >
                    {{ skill }}
                  </span>
                  <span v-if="candidate.missingSkills.length === 0" class="text-xs text-slate-400 italic">满足所有必备技能</span>
                </div>
              </div>

              <!-- Suggested HR action -->
              <div class="bg-slate-100/80 border border-slate-200/40 rounded-xl p-3.5 flex items-start gap-2 text-xs font-medium">
                <svg class="w-4.5 h-4.5 text-slate-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-12-12 9 9 0 0112 12z" />
                </svg>
                <div class="leading-relaxed">
                  <span class="font-bold text-slate-700 block mb-0.5">建议动作：</span>
                  <span class="text-slate-600 font-semibold">{{ candidate.recommendedAction }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom: Key Evidences Excerpt references -->
          <div v-if="candidate.evidenceItems.length > 0" class="border-t border-slate-200/80 pt-5 mt-4">
            <details class="group bg-white border border-slate-200/60 rounded-2xl overflow-hidden shadow-sm">
              <summary class="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-50 select-none font-bold text-xs text-slate-700">
                <span class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  候选人画像能力证据与原始材料 ({{ candidate.evidenceItems.length }})
                </span>
                <svg class="w-4 h-4 text-slate-400 group-open:rotate-180 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              
              <div class="border-t border-slate-100 p-4 space-y-3 bg-slate-50/20 max-h-96 overflow-y-auto no-scrollbar">
                <div 
                  v-for="(evidence, eIdx) in candidate.evidenceItems" 
                  :key="eIdx"
                  class="bg-white border border-slate-200 rounded-xl p-4 space-y-2 shadow-xs"
                >
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-bold text-blue-700 bg-blue-50 border border-blue-100 px-2 py-0.5 rounded">
                      {{ evidence.capability }}
                    </span>
                    <span class="text-[10px] text-slate-400 font-bold">
                      确信度: {{ evidence.confidence }}% · {{ evidence.supports ? '支持结论' : '无法求证' }}
                    </span>
                  </div>
                  <blockquote class="text-xs italic text-slate-600 pl-3 border-l-2 border-slate-300 font-medium leading-relaxed">
                    “{{ evidence.excerpt }}”
                  </blockquote>
                </div>
              </div>
            </details>
          </div>

        </div>
      </div>
    </div>

    <!-- Node Approval Actions Banner (For Real Runs) -->
    <div v-if="hasPendingApprovals" class="bg-blue-50 border border-blue-100 rounded-2xl p-6 space-y-4">
      <h3 class="text-sm font-bold text-blue-900 flex items-center gap-2">
        <svg class="w-5 h-5 text-blue-600 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
        待 HR 人工决策审查
      </h3>
      <p class="text-xs text-blue-700">
        招聘决策工作流需要 HR 审查关键产出。确认无误后点击审查通过，以驱动 Agent 生成最终报告。
      </p>
      
      <div class="flex flex-wrap gap-3">
        <!-- Job Match Approval -->
        <div v-if="jobMatchApprovalPending" class="flex items-center gap-2">
          <button 
            type="button" 
            :disabled="jobMatchApproving || jobMatchApprovalSubmitted" 
            @click="approveJobMatch"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-sm transition-all cursor-pointer"
          >
            {{ jobMatchApproving ? '提交中…' : jobMatchApprovalSubmitted ? '岗位匹配已通过' : '通过岗位匹配审查' }}
          </button>
        </div>

        <!-- Decision Review Approval -->
        <div v-if="decisionReviewApprovalPending" class="flex items-center gap-2">
          <button 
            type="button" 
            :disabled="decisionReviewApproving || decisionReviewApprovalSubmitted" 
            @click="approveDecisionReview"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-sm transition-all cursor-pointer"
          >
            {{ decisionReviewApproving ? '提交中…' : decisionReviewApprovalSubmitted ? '决策审查已通过' : '通过决策规则审查' }}
          </button>
        </div>
      </div>
      <p v-if="jobMatchApprovalError" class="text-xs text-red-600 font-semibold">{{ jobMatchApprovalError }}</p>
      <p v-if="decisionReviewApprovalError" class="text-xs text-red-600 font-semibold">{{ decisionReviewApprovalError }}</p>
    </div>

    <!-- HR Final Report Card -->
    <div v-if="report" class="bg-indigo-900 text-white rounded-3xl p-8 space-y-6 shadow-xl">
      <div class="flex items-center justify-between border-b border-indigo-800 pb-4">
        <div>
          <span class="text-indigo-300 text-[10px] font-black uppercase tracking-wider">Node: hr_report</span>
          <h3 class="text-lg font-bold mt-0.5">HR 最终评估建议报告</h3>
        </div>
        <span class="px-2.5 py-1 bg-indigo-800 text-indigo-200 rounded-lg text-xs font-medium uppercase">
          {{ report.generation_mode }}
        </span>
      </div>

      <div class="space-y-4">
        <div>
          <h4 class="text-xs font-bold text-indigo-300 uppercase tracking-wider mb-2">报告摘要</h4>
          <p class="text-sm leading-relaxed text-indigo-100 font-medium">
            {{ report.executive_summary || 'Agent 已完成评估，未生成进一步摘要。' }}
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          <!-- Rankings -->
          <div class="bg-indigo-950/40 rounded-2xl p-5 border border-indigo-800/30">
            <h4 class="text-xs font-bold text-indigo-300 uppercase tracking-wider mb-3">候选人推荐排序</h4>
            <ol v-if="report.candidate_rankings.length" class="space-y-2.5">
              <li 
                v-for="(candidateId, index) in report.candidate_rankings" 
                :key="candidateId"
                class="flex items-center justify-between bg-indigo-950/60 rounded-xl p-3 border border-indigo-800/20"
              >
                <div class="flex items-center gap-2.5">
                  <span class="w-6 h-6 rounded-full bg-indigo-800/50 text-indigo-300 flex items-center justify-center font-bold text-xs">
                    {{ index + 1 }}
                  </span>
                  <span class="text-sm font-bold text-indigo-100">
                    {{ candidateLabel(candidateId) }}
                  </span>
                </div>
                <span class="text-xs font-semibold text-indigo-300">
                  {{ rankingScore(candidateId) }}
                </span>
              </li>
            </ol>
            <p v-else class="text-xs text-indigo-400 italic">报告未包含候选人排序。</p>
          </div>

          <!-- Gaps & Action -->
          <div class="bg-indigo-950/40 rounded-2xl p-5 border border-indigo-800/30 space-y-4">
            <div>
              <h4 class="text-xs font-bold text-indigo-300 uppercase tracking-wider mb-2">人才画像特征 / 缺口</h4>
              <ul v-if="report.talent_gaps.length" class="list-disc pl-4 space-y-1 text-xs text-indigo-200">
                <li v-for="gap in report.talent_gaps" :key="gap">{{ gap }}</li>
              </ul>
              <p v-else class="text-xs text-indigo-400 italic">未发现明显人才缺口。</p>
            </div>
            
            <div>
              <h4 class="text-xs font-bold text-indigo-300 uppercase tracking-wider mb-2">下一步建议动作</h4>
              <ul v-if="report.next_actions.length" class="list-disc pl-4 space-y-1 text-xs text-indigo-200">
                <li v-for="action in report.next_actions" :key="action">{{ action }}</li>
              </ul>
              <p v-else class="text-xs text-indigo-400 italic">无推荐的动作项。</p>
            </div>
          </div>
        </div>

        <!-- Human decision boundary notice -->
        <div class="flex items-center gap-3 bg-indigo-950/40 border border-indigo-800/30 rounded-2xl p-4 mt-4 text-xs text-indigo-200">
          <svg class="w-5 h-5 text-indigo-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-12-12 9 9 0 0112 12z" />
          </svg>
          <div>
            <strong class="text-indigo-100">人工最终决策边界提示：</strong>
            {{ report.requires_human_decision ? '本报告仅供决策参考，不代表已录用或已淘汰。最终录用流程始终保留人工边界。' : '本报告无特殊需人工特别审查事项。' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  approveDecisionReview as submitDecisionReviewApproval,
  approveJobMatchReview as submitJobMatchReviewApproval,
} from '../../../../shared/api/modules/agent';
import type {
  DecisionReviewSummary,
  JobMatchSummary,
  RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';
import { AgentNodeStatus } from '../../../../shared/agent/contracts';

const props = withDefaults(defineProps<{
  snapshot: RecruitmentRunSnapshot | null;
  candidateNames?: Record<number, string>;
  expandedId?: number | null;
}>(), {
  candidateNames: () => ({}),
  expandedId: null,
});

const emit = defineEmits<{
  (e: 'update:expandedId', id: number | null): void;
}>();

const expandedReportId = computed({
  get: () => props.expandedId,
  set: (val) => emit('update:expandedId', val),
});

// Static mock data fallback when snapshot is not available
const MOCK_CANDIDATES = [
  {
    id: 1,
    name: '陈晨',
    status: 'INTERVIEW_PENDING',
    score: 60.81,
    matchScore: 55.61,
    radar: { skill: 43.48, exp: 91.00, project: 43.48, edu: 82.00, risk: 70.00 },
    matchedSkills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'REST API', 'Tool Calling'],
    missingSkills: ['Git', 'LangGraph', 'AutoGen', 'CrewAI', 'MCP', 'Milvus', 'pgvector', 'Agent 状态持久化'],
    riskLevel: 'HIGH',
    decisionRisk: '必备技能未通过: Git。确信度 67.39% 低于阈值 70。',
    suggestedQuestions: [
      '在多 Agent 决策平台中，你是如何处理 PostgreSQL Run 持久化和故障恢复的？',
      '如何处理 SSE 事件流中的网络断开与状态同步问题？',
      '在使用 FastAPI 时，如何设计安全可靠的 API 权限审计拦截器？'
    ],
    findings: [
      { code: 'REQ_GIT_MISSING', severity: 'HIGH', summary: '必备技能未通过: Git。简历中未提及 Git 版本管理经验。' }
    ],
    evidenceItems: [
      { capability: 'FastAPI 智能应用开发', excerpt: '陈晨具有 30 个月 Python 智能应用开发经历，主要使用 FastAPI、PostgreSQL 和 Docker 交付企业应用。', supports: true, confidence: 95 },
      { capability: 'Agent 状态与 SSE 持久化', excerpt: '在企业招聘多 Agent 决策平台中，负责 Agent 工作流、RAG 检索、SSE 事件流和 PostgreSQL Run 持久化。', supports: true, confidence: 92 },
      { capability: '系统架构可审计设计', excerpt: '项目记录了节点状态、知识来源与工具执行摘要，并在模型异常时进入可审计的自动回退流程。', supports: true, confidence: 90 }
    ],
    recommendedAction: '安排初试。重点考察其 Git 工具链熟练度、团队协作流程以及 SSE 状态同步深度。'
  },
  {
    id: 2,
    name: '吴桐',
    status: 'AI_SCREENED',
    score: 45.40,
    matchScore: 37.00,
    radar: { skill: 17.39, exp: 85.67, project: 17.39, edu: 82.00, risk: 70.00 },
    matchedSkills: ['Python', 'FastAPI', 'PostgreSQL', 'Git'],
    missingSkills: ['REST API', 'Agent', 'RAG', 'Tool Calling', 'Docker', 'ChromaDB', '结构化输出'],
    riskLevel: 'MEDIUM',
    decisionRisk: '必备技能未通过: REST API, Agent 等。候选人画像缺少可量化成果。',
    suggestedQuestions: [
      '你提到了解 Agent 开发，但未能在匹配维度中通过 REST API 验证，请说明两者在架构上的协作细节？',
      '候选人画像中缺乏明确的加分项或可量化生产业绩，请结合你的项目进行补充？'
    ],
    findings: [
      { code: 'REQ_REST_API_MISSING', severity: 'MEDIUM', summary: '必备必备技能未通过: REST API, Agent, RAG 等。' },
      { code: 'ACHIEVEMENT_LACK', severity: 'LOW', summary: '画像匹配提示：候选人项目描述中缺乏可量化业务产出或系统性能指标。' }
    ],
    evidenceItems: [
      { capability: 'Python 开发经验', excerpt: '具有 24 个月 Python 开发经验，熟悉常用的关系型数据库连接。', supports: true, confidence: 85 }
    ],
    recommendedAction: '人工复核。重点考查其 REST API 规范及多 Agent 工作流理论，评估是否满足智能应用组的开发标准。'
  }
];

const displayCandidates = computed(() => {
  if (!props.snapshot) return MOCK_CANDIDATES;
  
  const jobMatches = props.snapshot.job_matches || {};
  const decisionReviews = props.snapshot.decision_reviews || {};
  const candidateProfiles = props.snapshot.candidate_profiles || {};
  
  return Object.values(jobMatches).map((match) => {
    const candidateId = match.candidate_id;
    const review = decisionReviews[String(candidateId)];
    const profile = candidateProfiles[String(candidateId)];
    
    // Determine risk level
    let riskLevel: 'HIGH' | 'MEDIUM' | 'LOW' = 'LOW';
    if (review) {
      if (review.findings.some(f => f.severity === 'HIGH')) riskLevel = 'HIGH';
      else if (review.findings.some(f => f.severity === 'MEDIUM')) riskLevel = 'MEDIUM';
    }
    
    // Construct decisionRisk
    let decisionRisk = '未发现关键风险项';
    if (review) {
      if (review.recommended_action) {
        decisionRisk = review.recommended_action;
      } else if (review.findings.length > 0) {
        decisionRisk = review.findings.map(f => f.summary).join('；');
      }
    }
    
    // Construct radar mapping
    const radar = {
      skill: match.dimension_scores.skill || match.dimension_scores.skills || match.dimension_scores.skill_match || 0,
      exp: match.dimension_scores.experience || match.dimension_scores.exp || 0,
      project: match.dimension_scores.projects || match.dimension_scores.project || 0,
      edu: match.dimension_scores.education || match.dimension_scores.edu || 0,
      risk: match.dimension_scores.risk || 0
    };

    // Extract detailed fields from profile evidence and findings
    const matchedSkills = match.matched_skills || [];
    const suggestedQuestions = match.suggested_interview_questions || [];
    const findings = review ? (review.findings || []) : [];
    const evidenceItems = profile ? (profile.evidence_items || []) : [];
    const recommendedAction = review?.recommended_action || match.recommended_action || '建议人工复核';

    return {
      id: candidateId,
      name: props.candidateNames[candidateId] || `候选人 #${candidateId}`,
      status: props.snapshot?.nodes.hr_report === AgentNodeStatus.COMPLETED ? 'AI_SCREENED' : 'INTERVIEW_PENDING',
      score: match.overall_score || 0,
      matchScore: match.job_match_score || 0,
      radar,
      matchedSkills,
      missingSkills: match.missing_skills || [],
      riskLevel,
      decisionRisk,
      suggestedQuestions,
      findings,
      evidenceItems,
      recommendedAction
    };
  }).sort((a, b) => b.score - a.score);
});

// Setup default expanded card
watch(displayCandidates, (candidates) => {
  if (candidates.length > 0 && props.expandedId === null) {
    emit('update:expandedId', candidates[0].id);
  }
}, { immediate: true });

function toggleReport(id: number) {
  expandedReportId.value = expandedReportId.value === id ? null : id;
}

// Format number utility
function formatNum(val: number | null): string {
  if (val === null || !Number.isFinite(val)) return '—';
  return val.toFixed(2);
}

// Form logic and approvals integration
const report = computed(() => props.snapshot?.report || null);
const jobMatchApproving = ref(false);
const jobMatchApprovalSubmitted = ref(false);
const jobMatchApprovalError = ref('');
const decisionReviewApproving = ref(false);
const decisionReviewApprovalSubmitted = ref(false);
const decisionReviewApprovalError = ref('');

const jobMatchApprovalPending = computed(() => {
  const snapshot = props.snapshot;
  if (!snapshot || snapshot.report !== null) return false;
  if (snapshot.nodes.hr_report !== AgentNodeStatus.WAITING) return false;
  return snapshot.nodes.job_match === AgentNodeStatus.NEEDS_REVIEW;
});

const decisionReviewApprovalPending = computed(() => {
  const snapshot = props.snapshot;
  if (!snapshot || snapshot.report !== null) return false;
  if (snapshot.nodes.hr_report !== AgentNodeStatus.WAITING) return false;
  return snapshot.nodes.decision_review === AgentNodeStatus.NEEDS_REVIEW;
});

const hasPendingApprovals = computed(() => jobMatchApprovalPending.value || decisionReviewApprovalPending.value);

watch(() => props.snapshot?.run_id, () => {
  jobMatchApproving.value = false;
  jobMatchApprovalSubmitted.value = false;
  jobMatchApprovalError.value = '';
  decisionReviewApproving.value = false;
  decisionReviewApprovalSubmitted.value = false;
  decisionReviewApprovalError.value = '';
});

async function approveJobMatch(): Promise<void> {
  if (!props.snapshot || jobMatchApproving.value) return;
  jobMatchApproving.value = true;
  jobMatchApprovalSubmitted.value = false;
  jobMatchApprovalError.value = '';
  try {
    await submitJobMatchReviewApproval(props.snapshot.run_id);
    jobMatchApprovalSubmitted.value = true;
  } catch (error) {
    jobMatchApprovalError.value = error instanceof Error ? error.message : '岗位匹配审查提交失败，请稍后重试。';
  } finally {
    jobMatchApproving.value = false;
  }
}

async function approveDecisionReview(): Promise<void> {
  if (!props.snapshot || decisionReviewApproving.value) return;
  decisionReviewApproving.value = true;
  decisionReviewApprovalSubmitted.value = false;
  decisionReviewApprovalError.value = '';
  try {
    await submitDecisionReviewApproval(props.snapshot.run_id);
    decisionReviewApprovalSubmitted.value = true;
  } catch (error) {
    decisionReviewApprovalError.value = error instanceof Error ? error.message : '决策审查提交失败，请稍后重试。';
  } finally {
    decisionReviewApproving.value = false;
  }
}

function candidateLabel(candidateId: number): string {
  return props.candidateNames[candidateId] || `候选人 #${candidateId}`;
}

function rankingScore(candidateId: number): string {
  const match = props.snapshot?.job_matches[String(candidateId)];
  return match ? `${formatNum(match.overall_score)}分` : '无确定性评分';
}
</script>

<style scoped>
.expand-content { transition: max-height 0.4s ease-in-out, opacity 0.3s ease-in-out; }

[data-theme="dark"] .bg-white { background-color: #1e293c !important; }
[data-theme="dark"] .bg-slate-50\/30 { background-color: rgba(15, 23, 42, 0.3) !important; }
[data-theme="dark"] .bg-slate-50\/20 { background-color: rgba(15, 23, 42, 0.2) !important; }
[data-theme="dark"] .bg-slate-100\/80 { background-color: rgba(51, 65, 85, 0.8) !important; }
[data-theme="dark"] .bg-blue-50 { background-color: #1a2744 !important; }
[data-theme="dark"] .bg-red-50 { background-color: #450a0a !important; }
[data-theme="dark"] .bg-red-50\/50 { background-color: rgba(69, 10, 10, 0.5) !important; }
[data-theme="dark"] .bg-amber-50 { background-color: #451a02 !important; }
[data-theme="dark"] .bg-emerald-50 { background-color: #052e15 !important; }
[data-theme="dark"] .bg-indigo-100 { background-color: #312e81 !important; }
[data-theme="dark"] .text-slate-800 { color: #e2e8f0 !important; }
[data-theme="dark"] .text-slate-700 { color: #cbd5e1 !important; }
[data-theme="dark"] .text-slate-600 { color: #94a3b8 !important; }
[data-theme="dark"] .text-slate-500 { color: #94a3b8 !important; }
[data-theme="dark"] .text-slate-400 { color: #64748b !important; }
[data-theme="dark"] .text-indigo-600 { color: #a5b4fc !important; }
[data-theme="dark"] .text-blue-600 { color: #93c5fd !important; }
[data-theme="dark"] .text-blue-700 { color: #93c5fd !important; }
[data-theme="dark"] .text-blue-900 { color: #bfdbfe !important; }
[data-theme="dark"] .text-red-600 { color: #fca5a5 !important; }
[data-theme="dark"] .text-red-800 { color: #fecaca !important; }
[data-theme="dark"] .text-amber-600 { color: #fcd34d !important; }
[data-theme="dark"] .text-emerald-700 { color: #6ee7b8 !important; }
[data-theme="dark"] .text-blue-500 { color: #60a5fa !important; }
[data-theme="dark"] .border-slate-200 { border-color: #334155 !important; }
[data-theme="dark"] .border-slate-200\/60 { border-color: rgba(51, 65, 85, 0.6) !important; }
[data-theme="dark"] .border-slate-200\/80 { border-color: rgba(51, 65, 85, 0.8) !important; }
[data-theme="dark"] .border-slate-200\/40 { border-color: rgba(51, 65, 85, 0.4) !important; }
[data-theme="dark"] .border-slate-100 { border-color: #1e293c !important; }
[data-theme="dark"] .border-red-100 { border-color: #7f1d1d !important; }
[data-theme="dark"] .border-amber-100 { border-color: #78350f !important; }
[data-theme="dark"] .border-blue-100 { border-color: #1e3a5f !important; }
[data-theme="dark"] .border-emerald-100 { border-color: #064e3b !important; }
[data-theme="dark"] .hover\:bg-slate-50:hover { background-color: #1e293c !important; }
[data-theme="dark"] .border-l-slate-300 { border-left-color: #475569 !important; }
</style>
