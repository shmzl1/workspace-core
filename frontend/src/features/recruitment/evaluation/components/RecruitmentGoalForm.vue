<template>
  <form class="goal-form" @submit.prevent="submit">
    <div class="goal-form__heading">
      <div>
        <span>企业招聘目标</span>
        <h2>配置本次策略规划</h2>
      </div>
      <p v-if="selectedJob">{{ selectedJob.department }} · {{ selectedJob.title }}</p>
    </div>

    <div class="goal-form__grid">
      <label class="goal-form__wide">
        <span>岗位</span>
        <select v-model.number="model.job_id" :disabled="disabled">
          <option :value="0">请选择真实岗位</option>
          <option v-for="job in jobs" :key="job.id" :value="job.id">
            {{ job.title }}（{{ job.department }}）
          </option>
        </select>
      </label>
      <label><span>目标招聘人数</span><input v-model.number="model.target_headcount" type="number" min="1" :disabled="disabled" /></label>
      <label><span>截止日期</span><input v-model="model.deadline" type="date" :disabled="disabled" /></label>
      <label class="goal-form__wide"><span>必备技能（逗号分隔）</span><input v-model="model.required_skills" :disabled="disabled" /></label>
      <label class="goal-form__wide"><span>加分技能（逗号分隔）</span><input v-model="model.preferred_skills" :disabled="disabled" /></label>
      <label><span>最低经验（月）</span><input v-model.number="model.min_experience_months" type="number" min="0" :disabled="disabled" /></label>
      <label><span>评分阈值</span><input v-model.number="model.score_threshold" type="number" min="0" max="100" :disabled="disabled" /></label>
      <label><span>可信度阈值</span><input v-model.number="model.confidence_threshold" type="number" min="0" max="100" :disabled="disabled" /></label>
      <label>
        <span>紧急程度</span>
        <select v-model="model.urgency" :disabled="disabled">
          <option value="LOW">低</option><option value="NORMAL">正常</option><option value="HIGH">高</option><option value="CRITICAL">紧急</option>
        </select>
      </label>
      <label><span>可选薪资预算</span><input v-model="model.optional_salary_budget" type="number" min="0" placeholder="可留空" :disabled="disabled" /></label>
    </div>

    <fieldset :disabled="disabled || !model.job_id">
      <legend>候选人（至少一名）</legend>
      <p v-if="!model.job_id" class="goal-form__hint">请先选择岗位。</p>
      <p v-else-if="jobApplications.length === 0" class="goal-form__hint">当前岗位没有可选候选人申请。</p>
      <label v-for="application in jobApplications" :key="application.id" class="candidate-option">
        <input v-model="model.candidate_ids" type="checkbox" :value="application.candidate_id" />
        <span>{{ application.candidate_name || `候选人 #${application.candidate_id}` }}</span>
        <small>{{ application.current_stage }}</small>
      </label>
    </fieldset>

    <ul v-if="validationErrors.length" class="goal-form__errors">
      <li v-for="message in validationErrors" :key="message">{{ message }}</li>
    </ul>
    <button type="submit" :disabled="disabled">{{ disabled ? '多 Agent 评估运行中…' : '开始多 Agent 评估' }}</button>
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

<style scoped>
.goal-form { display:grid; gap:18px; padding:22px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:var(--color-surface); box-shadow:var(--shadow-card); }
.goal-form__heading { display:flex; align-items:flex-end; justify-content:space-between; gap:16px; }.goal-form__heading span { color:var(--color-primary); font-size:12px; font-weight:800; }.goal-form__heading h2 { margin:5px 0 0; }.goal-form__heading p { margin:0; color:var(--color-muted); }
.goal-form__grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; }.goal-form__wide { grid-column:span 2; } label { display:grid; gap:6px; color:var(--color-muted); font-size:13px; font-weight:700; } input,select { min-height:42px; padding:0 11px; border:1px solid var(--color-line); border-radius:var(--radius-sm); background:var(--color-surface); color:var(--color-text); }
fieldset { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; padding:14px; border:1px solid var(--color-line); border-radius:var(--radius-sm); } legend { padding:0 6px; color:var(--color-text); font-weight:800; }.candidate-option { display:grid; grid-template-columns:auto 1fr auto; align-items:center; padding:10px; border-radius:10px; background:var(--color-surface-soft); }.candidate-option input { min-height:auto; }.candidate-option small,.goal-form__hint { color:var(--color-subtle); }
.goal-form__errors { margin:0; padding:12px 28px; border-radius:var(--radius-sm); background:var(--color-status-error-bg); color:var(--color-status-error-text); }.goal-form button { min-height:44px; border-radius:var(--radius-sm); background:var(--color-primary); color:#fff; font-weight:800; }.goal-form button:disabled { opacity:.6; cursor:wait; }
@media (max-width:1000px) { .goal-form__grid { grid-template-columns:repeat(2,minmax(0,1fr)); } fieldset { grid-template-columns:1fr 1fr; } } @media (max-width:640px) { .goal-form__grid,fieldset { grid-template-columns:1fr; }.goal-form__wide { grid-column:auto; }.goal-form__heading { align-items:flex-start; flex-direction:column; } }
</style>

