<template>
  <section class="min-h-screen text-slate-800 space-y-8 pb-20">
    <!-- Local Dashboard Header -->
    <header class="reveal-section" style="animation-delay: 0s">
      <div class="recruitment-hover-card bg-white rounded-3xl border border-slate-200 px-8 py-6 flex items-center justify-between shadow-sm">
        <div>
          <h1 class="text-2xl font-black text-slate-900 tracking-tight">AI 招聘中心</h1>
          <p class="text-sm text-slate-500 mt-1">围绕招聘目标生成策略、画像匹配、最终决定始终保留人工边界。</p>
        </div>
        <div class="flex items-center gap-3">
          <span class="px-3 py-1 bg-blue-50 text-blue-600 border border-blue-100 rounded-full text-xs font-bold uppercase tracking-wider">
            PostgreSQL Run · 实时 SSE
          </span>
        </div>
      </div>
    </header>

    <PermissionDenied v-if="permissionDenied" description="当前账号缺少 agent.hr.use 权限。" />
    <LoadingState v-else-if="contextLoading" message="正在读取真实岗位与候选人…" />
    <ErrorState v-else-if="contextError" title="招聘上下文加载失败" :message="contextError" retry-label="重新加载" @retry="loadContext" />
    
    <template v-else>
      <!-- Section 1: Goal Configuration Form -->
      <div class="reveal-section" style="animation-delay: 0.15s">
        <RecruitmentGoalForm
          :jobs="jobs"
          :applications="applications"
          :disabled="runBusy"
          @submit="start"
        />
      </div>

      <!-- Node/Workflow Run Errors -->
      <div v-if="error" class="reveal-section bg-red-50 border border-red-200 text-red-700 px-5 py-4 rounded-2xl text-sm flex items-center gap-3 shadow-sm" style="animation-delay: 0.3s">
        <svg class="w-5 h-5 text-red-500 flex-shrink-0 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div>
          <strong class="font-bold">运行提示：</strong>
          <span>{{ error }}</span>
        </div>
      </div>

      <!-- Section 2: Top-Level Workflow Path (Horizontal Canvas) -->
      <div class="reveal-section" style="animation-delay: 0.45s">
        <MultiAgentWorkflowBoard
          :snapshot="snapshot"
          :selected-node="selectedNode"
          @select="handleNodeSelect"
        />
      </div>

      <!-- Section 3: Position Match & AI Review Unified Card (Collapsible) -->
      <div class="reveal-section" style="animation-delay: 0.6s">
        <Sprint23ResultsPanel
          :snapshot="snapshot"
          :candidate-names="candidateNames"
          v-model:expanded-id="activeReportId"
        />
      </div>

      <!-- Section 4: Checkable Candidate applications list -->
      <div class="reveal-section" style="animation-delay: 0.75s">
      <section class="recruitment-hover-card bg-white rounded-3xl shadow-sm border border-slate-200 p-8">
        <div class="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
          <h2 class="text-lg font-bold flex items-center gap-2 text-slate-900">
            <div class="w-1.5 h-6 bg-purple-500 rounded-full"></div>
            候选人列表
          </h2>
          <span class="text-xs text-slate-400 font-medium">勾选候选人可以批量标记为初筛通过</span>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-slate-200">
                <th class="py-4 px-4 w-12">
                  <input 
                    type="checkbox" 
                    class="w-4 h-4 rounded border-slate-300 text-purple-600 focus:ring-purple-500 cursor-pointer" 
                    @change="toggleSelectAll"
                    :checked="isAllSelected"
                  />
                </th>
                <th class="py-4 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">候选人</th>
                <th class="py-4 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">当前状态</th>
                <th class="py-4 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider">综合得分</th>
                <th class="py-4 px-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="candidate in candidatesList" 
                :key="candidate.id" 
                class="border-b border-slate-100 hover:bg-slate-50 transition-colors"
              >
                <td class="py-4 px-4">
                  <input 
                    type="checkbox" 
                    class="w-4 h-4 rounded border-slate-300 text-purple-600 focus:ring-purple-500 cursor-pointer"
                    :checked="selectedCandidates.includes(candidate.id)"
                    @change="toggleCandidate(candidate.id)"
                  />
                </td>
                <td class="py-4 px-4 font-bold text-slate-800">{{ candidate.name }}</td>
                <td class="py-4 px-4">
                  <span class="px-2.5 py-1 bg-slate-100 text-slate-600 rounded-md text-xs font-bold uppercase tracking-wider">
                    {{ candidate.status }}
                  </span>
                </td>
                <td class="py-4 px-4 font-bold text-indigo-600">
                  {{ candidate.score ? candidate.score.toFixed(2) + '分' : '—' }}
                </td>
                <td class="py-4 px-4 text-right">
                  <button 
                    @click="scrollToReport(candidate.id)"
                    class="text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors cursor-pointer"
                  >
                    查看画像
                  </button>
                </td>
              </tr>
              <tr v-if="candidatesList.length === 0">
                <td colspan="5" class="py-8 text-center text-slate-400 text-sm font-medium">
                  当前暂无候选人评估数据
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      </div>
    </template>

    <!-- Floating Action Bar at the Bottom -->
    <div v-if="selectedCandidates.length > 0" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 animate-[translateY_0.2s_ease-out]">
      <div class="bg-slate-900 text-white px-6 py-4 rounded-full shadow-2xl flex items-center gap-6">
        <span class="text-sm font-medium">已选择 {{ selectedCandidates.length }} 名候选人</span>
        <div class="w-px h-4 bg-slate-700"></div>
        <button 
          @click="handleImport"
          :disabled="advancingCandidates"
          class="bg-indigo-500 hover:bg-indigo-400 disabled:bg-indigo-300 text-white px-5 py-2 rounded-full text-sm font-bold transition-colors cursor-pointer"
        >
          {{ advancingCandidates ? '正在处理…' : '初筛通过' }}
        </button>
      </div>
    </div>

    <!-- Success Toast Notification -->
    <div 
      v-if="toastVisible" 
      class="fixed top-20 left-1/2 -translate-x-1/2 z-50 transition-all duration-300"
    >
      <div class="bg-emerald-50 border border-emerald-200 text-emerald-800 px-6 py-3 rounded-xl shadow-lg flex items-center gap-3">
        <svg class="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span class="font-bold text-sm">已成功导入候选人池</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ApiClientError } from '../../../shared/api/apiClient';
import { 
  fetchApplications, 
  fetchJobs, 
  advanceCandidateStage,
  type CandidateApplicationListItem 
} from '../../../shared/api/modules/recruitment';
import type { Job } from '../../../shared/api/types';
import ErrorState from '../../../shared/components/feedback/ErrorState.vue';
import LoadingState from '../../../shared/components/feedback/LoadingState.vue';
import PermissionDenied from '../../../shared/components/feedback/PermissionDenied.vue';
import MultiAgentWorkflowBoard from './components/MultiAgentWorkflowBoard.vue';
import RecruitmentGoalForm from './components/RecruitmentGoalForm.vue';
import Sprint23ResultsPanel from './components/Sprint23ResultsPanel.vue';
import { useRecruitmentAgentRun } from './composables/useRecruitmentAgentRun';

const route = useRoute();
const jobs = ref<Job[]>([]);
const applications = ref<CandidateApplicationListItem[]>([]);
const contextLoading = ref(true);
const contextError = ref('');
const permissionDenied = ref(false);
const selectedNode = ref('recruitment_strategy');

const selectedCandidates = ref<number[]>([]);
const activeReportId = ref<number | null>(null);
const toastVisible = ref(false);
const advancingCandidates = ref(false);

const { snapshot, events, loading, streaming, error, isTerminal, start, restore } = useRecruitmentAgentRun();
const runBusy = computed(() => loading.value || Boolean(snapshot.value && !isTerminal.value));

const candidateNames = computed(() => applications.value.reduce<Record<number, string>>((names, application) => {
  if (application.candidate_name) names[application.candidate_id] = application.candidate_name;
  return names;
}, {}));

// Dynamic candidates table mapping real run or mock context
const candidatesList = computed(() => {
  if (!snapshot.value) {
    return [
      { id: 1, name: '陈晨', status: 'INTERVIEW_PENDING', score: 60.81, applicationId: null },
      { id: 2, name: '吴桐', status: 'AI_SCREENED', score: 45.40, applicationId: null },
    ];
  }
  
  const jobMatches = snapshot.value.job_matches || {};
  return Object.values(jobMatches).map((match) => {
    const candidateId = match.candidate_id;
    const app = applications.value.find(
      (a) => a.candidate_id === candidateId && a.job_id === snapshot.value!.goal.job_id
    );
    return {
      id: candidateId,
      name: candidateNames.value[candidateId] || `候选人 #${candidateId}`,
      status: app ? app.current_stage : 'INTERVIEW_PENDING',
      score: match.overall_score || 0,
      applicationId: app?.id || null,
    };
  }).sort((a, b) => b.score - a.score);
});

// Selection logic
const isAllSelected = computed(() => {
  return candidatesList.value.length > 0 && selectedCandidates.value.length === candidatesList.value.length;
});

function toggleSelectAll(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.checked) {
    selectedCandidates.value = candidatesList.value.map((c) => c.id);
  } else {
    selectedCandidates.value = [];
  }
}

function toggleCandidate(id: number) {
  if (selectedCandidates.value.includes(id)) {
    selectedCandidates.value = selectedCandidates.value.filter((cid) => cid !== id);
  } else {
    selectedCandidates.value.push(id);
  }
}

function scrollToReport(id: number) {
  activeReportId.value = id;
  // Scroll dynamically to result panel
  setTimeout(() => {
    const element = document.querySelector('.bg-teal-500');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, 100);
}

// Bulk advance candidate applications to candidate pool
async function handleImport() {
  if (selectedCandidates.value.length === 0) return;
  
  advancingCandidates.value = true;
  try {
    if (snapshot.value) {
      // Real database integration
      const jobMatches = snapshot.value.job_matches || {};
      for (const candidateId of selectedCandidates.value) {
        const item = candidatesList.value.find(c => c.id === candidateId);
        if (item && item.applicationId) {
          // Extract scores if present in snapshot
          const match = jobMatches[String(candidateId)] || jobMatches[candidateId];
          const score_total = match?.overall_score ?? null;
          const score_breakdown = match ? {
            project: match.dimension_scores?.project || match.dimension_scores?.projects || 0,
            skill: match.dimension_scores?.skill || match.dimension_scores?.skills || match.dimension_scores?.skill_match || 0,
            education: match.dimension_scores?.education || match.dimension_scores?.edu || 0,
            experience: match.dimension_scores?.experience || match.dimension_scores?.exp || 0,
            risk: match.dimension_scores?.risk || 0,
            match_score: match.job_match_score || score_total || 0,
            overall_score: score_total || 0
          } : null;

          // Determine next stage
          // APPLIED -> AI_SCREENED to enter candidate pool
          // If already AI_SCREENED or beyond, do not change stage (use item.status) but update scores
          const targetStage = item.status === 'APPLIED' ? 'AI_SCREENED' : item.status;

          await advanceCandidateStage(item.applicationId, {
            to_stage: targetStage as any,
            note: '多 Agent 招聘决策评估完成，HR 批量审查导入候选人池并同步评分。',
            score_total,
            score_breakdown
          });
        }
      }
      await loadContext(); // Reload to refresh stages
    }
    
    // Show success toast
    toastVisible.value = true;
    setTimeout(() => { toastVisible.value = false; }, 3000);
    selectedCandidates.value = [];
  } catch (err) {
    console.error('Failed to bulk import candidate stage:', err);
    alert('部分候选人阶段更新失败，请稍后重试。');
  } finally {
    advancingCandidates.value = false;
  }
}

function handleNodeSelect(nodeName: string) {
  selectedNode.value = nodeName;
}

async function loadContext(): Promise<void> {
  contextLoading.value = true;
  contextError.value = '';
  permissionDenied.value = false;
  try {
    [jobs.value, applications.value] = await Promise.all([fetchJobs(), fetchApplications()]);
  } catch (cause) {
    if (cause instanceof ApiClientError && cause.status === 403) permissionDenied.value = true;
    else contextError.value = cause instanceof Error ? cause.message : '无法读取招聘岗位和候选人。';
  } finally {
    contextLoading.value = false;
  }
}

onMounted(async () => {
  await loadContext();
  const queryRunId = route.query.run_id;
  const runId = Array.isArray(queryRunId) ? queryRunId[0] : queryRunId;
  if (typeof runId === 'string' && runId) await restore(runId);
});
</script>

<style scoped>
/* ── 入场浮现动画 ── */
@keyframes revealSection {
  0% {
    opacity: 0;
    clip-path: inset(0 100% 0 0);
    transform: translateX(-12px);
  }
  99% {
    opacity: 1;
    clip-path: inset(0 0 0 0);
    transform: translateX(0);
  }
  100% {
    opacity: 1;
    clip-path: none;
    transform: translateX(0);
  }
}

.reveal-section {
  opacity: 0;
  animation: revealSection 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

[data-theme="dark"] .bg-white { background-color: #1e293c !important; }
[data-theme="dark"] .text-slate-900 { color: #e2e8f0 !important; }
[data-theme="dark"] .text-slate-800 { color: #e2e8f0 !important; }
[data-theme="dark"] .text-slate-700 { color: #cbd5e1 !important; }
[data-theme="dark"] .text-slate-600 { color: #94a3b8 !important; }
[data-theme="dark"] .text-slate-500 { color: #94a3b8 !important; }
[data-theme="dark"] .text-slate-400 { color: #64748b !important; }
[data-theme="dark"] .border-slate-200 { border-color: #334155 !important; }
[data-theme="dark"] .border-slate-100 { border-color: #1e293c !important; }
[data-theme="dark"] .border-slate-300 { border-color: #475569 !important; }
[data-theme="dark"] .bg-slate-100 { background-color: #334155 !important; }
[data-theme="dark"] .bg-blue-50 { background-color: #1a2744 !important; }
[data-theme="dark"] .text-blue-600 { color: #93c5fd !important; }
[data-theme="dark"] .text-blue-800 { color: #93c5fd !important; }
[data-theme="dark"] .border-blue-100 { border-color: #1e3a5f !important; }
[data-theme="dark"] .bg-red-50 { background-color: #450a0a !important; }
[data-theme="dark"] .border-red-200 { border-color: #7f1d1d !important; }
[data-theme="dark"] .text-red-700 { color: #fca5a5 !important; }
[data-theme="dark"] .text-red-500 { color: #f87171 !important; }
[data-theme="dark"] .text-indigo-600 { color: #a5b4fc !important; }
[data-theme="dark"] .bg-emerald-50 { background-color: #052e15 !important; }
[data-theme="dark"] .border-emerald-200 { border-color: #064e3b !important; }
[data-theme="dark"] .text-emerald-800 { color: #6ee7b8 !important; }
[data-theme="dark"] .text-emerald-500 { color: #34d399 !important; }
[data-theme="dark"] .text-purple-600 { color: #c4b5fd !important; }
[data-theme="dark"] .hover\:bg-slate-50:hover { background-color: #1e293c !important; }
</style>
