<template>
  <form class="bg-gradient-to-b from-white to-slate-50/50 rounded-2xl shadow-sm border border-slate-200/80 p-6 space-y-5 text-xs transition-all hover:shadow-md" @submit.prevent="submit">
    <div class="flex items-center justify-between border-b border-slate-150 pb-3">
      <h2 class="text-sm font-bold flex items-center gap-2 text-slate-800">
        <div class="w-1 h-5 bg-blue-500 rounded-full animate-pulse"></div>
        配置本次策略规划
      </h2>
      <span v-if="selectedJob" class="px-2.5 py-0.5 bg-blue-50 text-blue-600 border border-blue-100 rounded-full text-[10px] font-bold">
        {{ selectedJob.department }}
      </span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Job selection -->
      <div class="md:col-span-2">
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">岗位</label>
        <select 
          v-model.number="model.job_id" 
          :disabled="disabled"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all cursor-pointer shadow-xs"
        >
          <option :value="0">请选择真实岗位</option>
          <option v-for="job in jobs" :key="job.id" :value="job.id">
            {{ job.title }}（{{ job.department }}）
          </option>
        </select>
      </div>

      <!-- Target headcount -->
      <div>
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">目标招聘人数</label>
        <input 
          v-model.number="model.target_headcount" 
          type="number" 
          min="1" 
          :disabled="disabled"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
        />
      </div>

      <!-- Deadline -->
      <div>
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">截止日期</label>
        <input 
          v-model="model.deadline" 
          type="date" 
          :disabled="disabled"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
        />
      </div>

      <!-- Minimum Experience -->
      <div>
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">最低经验（月）</label>
        <input 
          v-model.number="model.min_experience_months" 
          type="number" 
          min="0" 
          :disabled="disabled"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
        />
      </div>

      <!-- Urgency -->
      <div>
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">紧急程度</label>
        <select 
          v-model="model.urgency" 
          :disabled="disabled"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all cursor-pointer shadow-xs"
        >
          <option value="LOW">低</option>
          <option value="NORMAL">正常</option>
          <option value="HIGH">高</option>
          <option value="CRITICAL">紧急</option>
        </select>
      </div>

      <!-- Required Skills -->
      <div class="md:col-span-2">
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">必备技能 (英文逗号分隔)</label>
        <input 
          v-model="model.required_skills" 
          :disabled="disabled"
          placeholder="e.g. Python, FastAPI, Git, Docker"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
        />
      </div>

      <!-- Optional Budget -->
      <div>
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">可选薪资预算</label>
        <input 
          v-model="model.optional_salary_budget" 
          type="number" 
          min="0" 
          placeholder="可留空" 
          :disabled="disabled"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
        />
      </div>

      <!-- Score Threshold -->
      <div>
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">评分阈值</label>
        <input 
          v-model.number="model.score_threshold" 
          type="number" 
          min="0" 
          max="100" 
          :disabled="disabled"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
        />
      </div>

      <!-- Confidence Threshold -->
      <div>
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">可信度阈值</label>
        <input 
          v-model.number="model.confidence_threshold" 
          type="number" 
          min="0" 
          max="100" 
          :disabled="disabled"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
        />
      </div>

      <!-- Preferred Skills -->
      <div class="md:col-span-3">
        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">加分技能 (英文逗号分隔)</label>
        <input 
          v-model="model.preferred_skills" 
          :disabled="disabled"
          placeholder="e.g. Kubernetes, PyTorch, LangChain"
          class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-xs"
        />
      </div>
    </div>

    <!-- Candidate checklist -->
    <div class="border border-slate-150 rounded-xl p-4 bg-slate-50/50">
      <h3 class="text-xs font-bold text-slate-800 mb-3 flex items-center gap-1.5">
        <svg class="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        选择评估候选人
      </h3>
      
      <!-- Premium Block-based Empty State when no position selected -->
      <div v-if="!model.job_id" class="block w-full border border-dashed border-slate-200 rounded-xl py-8 px-4 text-center bg-white/60 mt-1 select-none">
        <div class="w-9 h-9 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center shadow-xs mx-auto mb-3">
          <svg class="w-4 h-4 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
          </svg>
        </div>
        <h4 class="block w-full text-xs font-bold text-slate-700 text-center">等待选择评估岗位</h4>
        <p class="block w-full text-[10px] text-slate-400 mt-1.5 leading-relaxed text-center break-normal whitespace-normal">
          请在上方“岗位”下拉菜单中选择一个招聘职位，系统将在此处自动加载与该岗位匹配的所有候选人简历申请。
        </p>
      </div>

      <!-- Premium Block-based Empty State when no applications are seeded -->
      <div v-else-if="jobApplications.length === 0" class="block w-full border border-dashed border-slate-200 rounded-xl py-8 px-4 text-center bg-white/60 mt-1 select-none">
        <div class="w-9 h-9 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center shadow-xs mx-auto mb-3">
          <svg class="w-4.5 h-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h4 class="block w-full text-xs font-bold text-slate-600 text-center">该岗位暂无待匹配候选人</h4>
        <p class="block w-full text-[10px] text-slate-400 mt-1.5 leading-relaxed text-center break-normal whitespace-normal">
          该岗位在数据库中暂无投递申请。您可以前往“候选人池”上传新简历匹配此岗位。
        </p>
      </div>
      
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        <label 
          v-for="application in jobApplications" 
          :key="application.id" 
          class="flex items-center gap-2.5 bg-white border border-slate-200 rounded-lg p-2.5 cursor-pointer hover:border-blue-400 hover:shadow-sm transition-all"
        >
          <input 
            v-model="model.candidate_ids" 
            type="checkbox" 
            :value="application.candidate_id"
            class="w-3.5 h-3.5 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
          />
          <div class="min-w-0 flex-1 leading-tight">
            <span class="block text-xs font-bold text-slate-800 truncate">
              {{ application.candidate_name || `候选人 #${application.candidate_id}` }}
            </span>
            <span class="block text-[9px] font-semibold text-slate-400 uppercase tracking-wider mt-0.5">
              {{ application.current_stage }}
            </span>
          </div>
        </label>
      </div>
    </div>

    <!-- Validation errors -->
    <div v-if="validationErrors.length" class="bg-red-50 border border-red-100 rounded-lg p-3 text-[11px] text-red-600">
      <h4 class="font-bold mb-0.5">请修正以下错误：</h4>
      <ul class="list-disc pl-4 space-y-0.5">
        <li v-for="message in validationErrors" :key="message">{{ message }}</li>
      </ul>
    </div>

    <!-- Submit button -->
    <button 
      type="submit" 
      :disabled="disabled || !model.job_id || model.candidate_ids.length === 0"
      class="w-full flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-100 disabled:text-slate-400 disabled:border-slate-200/50 border border-transparent disabled:cursor-not-allowed text-white font-bold py-2.5 px-4 rounded-xl text-xs shadow-xs transition-all cursor-pointer"
    >
      <svg v-if="disabled" class="animate-spin h-4 w-4 text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>{{ submitText }}</span>
    </button>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import type { Job } from '../../../../shared/api/types';
import type { CandidateApplicationListItem } from '../../../../shared/api/modules/recruitment';
import type { RecruitmentRunRequest, RecruitmentUrgency } from '../../../../shared/agent/contracts';

const props = defineProps<{ jobs: Job[]; applications: CandidateApplicationListItem[]; disabled?: boolean }>();
const emit = defineEmits<{ submit: [payload: RecruitmentRunRequest] }>();

const model = reactive({
  job_id: 0,
  target_headcount: 1,
  deadline: '',
  required_skills: '',
  preferred_skills: '',
  min_experience_months: 0,
  score_threshold: 70,
  confidence_threshold: 70,
  urgency: 'NORMAL' as RecruitmentUrgency,
  optional_salary_budget: '',
  candidate_ids: [] as number[],
});
const validationErrors = ref<string[]>([]);
const selectedJob = computed(() => props.jobs.find((job) => job.id === model.job_id) || null);
const jobApplications = computed(() => props.applications.filter((item) => item.job_id === model.job_id));

const submitText = computed(() => {
  if (props.disabled) return '多 Agent 评估运行中…';
  if (!model.job_id) return '请先在上方选择岗位';
  if (model.candidate_ids.length === 0) return '请勾选需要评估的候选人';
  return '开始多 Agent 评估';
});

watch(() => model.job_id, () => {
  model.candidate_ids = [];
  const job = selectedJob.value;
  if (!job) return;
  model.required_skills = job.required_skills.join(', ');
  model.preferred_skills = job.preferred_skills.join(', ');
  model.min_experience_months = job.min_experience_months;
  validationErrors.value = [];
});

function submit(): void {
  const job = selectedJob.value;
  const errors: string[] = [];
  if (!job) errors.push('必须选择岗位。');
  if (model.candidate_ids.length === 0) errors.push('至少选择一名候选人。');
  if (model.target_headcount <= 0) errors.push('目标招聘人数必须大于 0。');
  if (model.min_experience_months < 0) errors.push('最低经验月数不能小于 0。');
  if (!inThreshold(model.score_threshold) || !inThreshold(model.confidence_threshold)) errors.push('评分与可信度阈值必须位于 0～100。');
  validationErrors.value = errors;
  if (!job || errors.length) return;
  const salaryBudget = model.optional_salary_budget.trim() === '' ? null : Number(model.optional_salary_budget);
  emit('submit', {
    goal: {
      job_id: job.id,
      job_title: job.title,
      department: job.department,
      target_headcount: model.target_headcount,
      deadline: model.deadline || null,
      required_skills: splitSkills(model.required_skills),
      preferred_skills: splitSkills(model.preferred_skills),
      min_experience_months: model.min_experience_months,
      score_threshold: model.score_threshold,
      confidence_threshold: model.confidence_threshold,
      urgency: model.urgency,
      optional_salary_budget: salaryBudget !== null && Number.isFinite(salaryBudget) ? salaryBudget : null,
    },
    candidate_ids: [...model.candidate_ids],
  });
}

function splitSkills(value: string): string[] {
  return value.split(/[,，]/).map((item) => item.trim()).filter(Boolean);
}

function inThreshold(value: number): boolean {
  return Number.isFinite(value) && value >= 0 && value <= 100;
}
</script>
