<template>
  <div class="candidate-pool">
    <LoadingState v-if="loading" message="正在加载候选人数据..." detail="正在读取招聘候选人与申请信息" />

    <PermissionDenied
      v-else-if="permissionDenied"
      description="你当前的角色无权访问候选人池，如需协助请联系 HR 管理员。"
    />

    <section v-else-if="serviceError" class="service-error">
      <div>
        <strong>{{ serviceErrorTitle }}</strong>
        <span>{{ serviceError }}</span>
      </div>
      <button class="btn" @click="loadCandidatePool()">重新加载</button>
    </section>

    <template v-else>
      <section class="candidate-pool__hero">
        <div>
          <p class="candidate-pool__eyebrow">招聘决策</p>
          <h2>候选人池</h2>
          <p>集中查看候选人评分、岗位匹配度、风险标签与下一步推荐动作。</p>
        </div>
        <div class="candidate-pool__actions">
          <input
            ref="resumeFileInput"
            type="file"
            accept=".pdf,application/pdf"
            multiple
            hidden
            @change="handleResumeFiles"
          />

          <button class="btn btn--primary" @click="applySmartFilter">
            <span class="material-symbols-outlined">auto_awesome</span>
            智能筛选
          </button>
          <button class="btn" @click="sortByScore">
            <span class="material-symbols-outlined">sort</span>
            按 AI 评分排序
          </button>
          <button class="btn" :class="{ 'btn--active': highMatchOnly }" @click="toggleHighMatch">
            <span class="material-symbols-outlined">verified</span>
            只看高匹配候选人
          </button>
        </div>
      </section>

      <!-- Job Filter Dropdown -->
      <section v-if="jobs.length > 0" class="job-filter-bar">
        <label for="job-select">
          <span class="material-symbols-outlined">work</span> 
          选择展示岗位：
        </label>
        <select id="job-select" v-model="selectedJobId" class="job-select">
          <option :value="null">全部岗位</option>
          <option v-for="job in jobs" :key="job.id" :value="job.id">
            {{ formatJobLabel(job) }}
          </option>
        </select>
      </section>

      <EmptyState
        v-if="isEmpty"
        title="暂无候选人"
        description="当前岗位还没有候选人申请，请先发布岗位或导入简历。"
      />

      <p v-if="evaluationNotice" class="notice">{{ evaluationNotice }}</p>

      <section class="candidate-pool__summary">
        <article v-for="item in summaryCards" :key="item.label" class="metric-card">
          <span class="material-symbols-outlined">{{ item.icon }}</span>
          <div>
            <strong>{{ item.value }}</strong>
            <small>{{ item.label }}</small>
          </div>
        </article>
      </section>

      <section class="candidate-pool__content">
        <div class="candidate-pool__left">
          <div class="candidate-table-card">
            <div class="candidate-table-card__header">
              <div>
                <h3>候选人列表</h3>
                <p>{{ filterHint }}</p>
              </div>
              <div style="display: flex; align-items: center; gap: 12px;">
                <button 
                  class="btn btn--outline" 
                  style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px; border: 1px solid var(--color-line); border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer; background: var(--color-surface); transition: all 0.2s ease;"
                  :disabled="importing" 
                  @click="openResumeFilePicker"
                >
                  <span class="material-symbols-outlined" style="font-size: 16px;">person_add</span>
                  {{ importing ? '导入中…' : '新增候选人' }}
                </button>
                <span>{{ visibleCandidates.length }} 人</span>
              </div>
            </div>

            <EmptyState
              v-if="visibleCandidates.length === 0 && !isEmpty"
              title="当前筛选无候选人"
              :description="emptyFilterMessage"
            />
            <div v-else class="candidate-table">
              <button
                v-for="candidate in visibleCandidates"
                :key="candidate.id"
                class="candidate-row"
                :class="{ 'candidate-row--selected': selectedId === candidate.id }"
                @click="selectCandidate(candidate)"
              >
                <span class="candidate-row__name">
                  <strong>{{ candidate.name }}</strong>
                  <small>{{ candidate.location }} · {{ candidate.availableIn }}</small>
                </span>
                <span>{{ candidate.role }}</span>
                <span><em :class="stageClass(candidate.stage)">{{ candidate.stage }}</em></span>
                <span class="score">{{ formatScore(computedScore(candidate)) }}</span>
                <span v-if="candidate.match !== null">
                  <span class="match-bar"><i :style="{ width: `${candidate.match}%` }"></i></span>
                  <small>置信度：{{ candidate.match }}%</small>
                </span>
                <span v-else class="text-on-surface-variant">待评估</span>
              </button>
            </div>
          </div>

          <section v-if="canScoreCandidate" class="weight-sandbox weight-sandbox--inline">
            <div class="weight-sandbox__header">
              <h3><span class="material-symbols-outlined">tune</span>评分维度权重调整</h3>
              <button class="weight-sandbox__reset" @click="resetWeights">
                <span class="material-symbols-outlined">restart_alt</span>
                恢复默认
              </button>
            </div>
            <div class="weight-sandbox__sliders">
              <div v-for="dim in weightDimensions" :key="dim.key" class="weight-slider">
                <div class="weight-slider__header">
                  <label>{{ dim.label }}</label>
                  <span class="weight-slider__value">{{ weights[dim.key] }}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  :value="weights[dim.key]"
                  class="weight-slider__input"
                  @input="(event: Event) => updateWeight(dim.key, Number((event.target as HTMLInputElement).value))"
                />
              </div>
            </div>
          </section>
        </div>

        <aside v-if="selectedCandidate" class="candidate-detail-card">
          <div class="candidate-detail-card__header">
            <div>
              <p>AI 综合评估</p>
              <h3>{{ selectedCandidate.name }}</h3>
              <small>{{ selectedCandidate.role }} · {{ selectedCandidate.stage }}</small>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
              <button 
                style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px; border: 1px solid var(--color-primary-soft); border-radius: 999px; font-size: 11px; font-weight: 800; cursor: pointer; background: var(--color-primary-soft); color: var(--color-primary); transition: all 0.2s ease; outline: none; margin-right: 2px;"
                :disabled="viewingResume"
                @click="viewResume(selectedCandidate.id, selectedCandidate.name)"
                onmouseover="this.style.background='rgba(36,85,245,0.15)'"
                onmouseout="this.style.background='var(--color-primary-soft)'"
              >
                <span class="material-symbols-outlined" style="font-size: 14px;">visibility</span>
                {{ viewingResume ? '载入中...' : '查看简历' }}
              </button>
              
              <div class="candidate-detail-card__score">
                <strong>{{ formatScore(computedScore(selectedCandidate)) }}</strong>
                <span>综合评分</span>
              </div>
            </div>
          </div>

          <div class="score-breakdown">
            <h4>评分维度</h4>
            <div v-for="dim in weightDimensions" :key="dim.key" class="score-breakdown__row">
              <span class="score-breakdown__label">{{ dim.label }}</span>
              <span class="score-breakdown__bar-bg">
                <span class="score-breakdown__bar" :style="{ width: `${getDimensionScore(selectedCandidate.id, dim.key)}%` }"></span>
              </span>
              <span class="score-breakdown__val">{{ getDimensionScore(selectedCandidate.id, dim.key) }}</span>
            </div>
          </div>

          <div class="detail-grid">
            <article>
              <span class="material-symbols-outlined">fact_check</span>
              <strong>评分依据</strong>
              <p>{{ selectedCandidate.reason }}</p>
            </article>
            <article>
              <span class="material-symbols-outlined">hub</span>
              <strong>技能匹配</strong>
              <p>{{ selectedCandidate.skillMatch }}</p>
            </article>
            <article>
              <span class="material-symbols-outlined">work_history</span>
              <strong>经验匹配</strong>
              <p>{{ selectedCandidate.experienceMatch }}</p>
            </article>
            <article>
              <span class="material-symbols-outlined">school</span>
              <strong>学历匹配</strong>
              <p>{{ selectedCandidate.educationMatch }}</p>
            </article>
            <article class="detail-grid__wide">
              <span class="material-symbols-outlined">warning</span>
              <strong>风险提示</strong>
              <p>{{ selectedCandidate.riskDetail }}</p>
            </article>
          </div>

          <div class="interview-advice">
            <div>
              <span class="material-symbols-outlined">record_voice_over</span>
              <strong>面试建议</strong>
            </div>
            <p>{{ selectedCandidate.interviewAdvice }}</p>
          </div>

          <div v-if="canManageStage" class="stage-management">
            <p><strong>当前阶段：</strong>{{ selectedCandidate.stage }}</p>
            <template v-if="nextStageOptions.length">
              <select v-model="targetStage" class="stage-select" :disabled="advancing">
                <option v-for="option in nextStageOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              <input
                v-model.trim="stageNote"
                class="stage-note"
                maxlength="2000"
                placeholder="可选备注"
                :disabled="advancing"
              />
              <button class="btn" :disabled="advancing || !targetStage" @click="advanceSelectedStage">
                <span class="material-symbols-outlined">trending_flat</span>
                {{ advancing ? '推进中……' : '推进阶段' }}
              </button>
            </template>
            <span v-else class="terminal-stage">当前阶段为终态，不能继续推进。</span>
          </div>

          <div class="candidate-detail-card__footer">
            <button v-if="canManageInterview" class="btn btn--primary" @click="scheduleInterview(selectedCandidate)">
              <span class="material-symbols-outlined">event_available</span>
              安排面试
            </button>
            <button v-if="canScoreCandidate" class="btn" :disabled="scoring" @click="refreshEvaluation(selectedCandidate)">
              <span class="material-symbols-outlined">article</span>
              {{ scoring ? '评估中...' : '查看评估依据' }}
            </button>
          </div>
        </aside>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import EmptyState from '../shared/components/feedback/EmptyState.vue';
import PermissionDenied from '../shared/components/feedback/PermissionDenied.vue';
import { advanceCandidateStage, fetchApplication, fetchApplications, fetchCandidates, fetchJobs, importCandidateResumes, scoreCandidate } from '../shared/api/modules/recruitment';
import { checkBackendHealth } from '../shared/api/modules/health';
import apiClient, { ApiClientError } from '../shared/api/apiClient';
import { useAuthStore } from '../features/auth/authStore';
import type { CandidateApplicationListItem } from '../shared/api/modules/recruitment';
import type { Candidate as ApiCandidate, CandidateScoreResponse, Job as ApiJob, PipelineStage } from '../shared/api/types';

const router = useRouter();
const { hasPermission } = useAuthStore();

type Candidate = {
  id: number;
  applicationId: number;
  jobId: number;
  name: string;
  role: string;
  stage: string;
  stageCode: PipelineStage;
  aiScore: number | null;
  match: number | null;
  riskLabel: string;
  riskLevel: 'low' | 'medium' | 'high';
  recommendedAction: string;
  location: string;
  availableIn: string;
  reason: string;
  skillMatch: string;
  experienceMatch: string;
  educationMatch: string;
  riskDetail: string;
  interviewAdvice: string;
  dimScores: Record<string, number>;
};

type WeightKey = 'project_experience' | 'skill_match' | 'education' | 'work_experience' | 'overall_quality';

const emit = defineEmits<{
  navigate: [view: string];
  'show-toast': [message: string];
}>();

const loading = ref(true);
const importing = ref(false);
const resumeFileInput = ref<HTMLInputElement | null>(null);
const scoring = ref(false);
const advancing = ref(false);
const permissionDenied = ref(false);
const candidates = ref<Candidate[]>([]);
const jobs = ref<ApiJob[]>([]);
const selectedJobId = ref<number | null>(null);
const selectedId = ref<number>(0);
const targetStage = ref<PipelineStage | ''>('');
const stageNote = ref('');
const highMatchOnly = ref(false);
const filterMode = ref<'all' | 'smart' | 'score'>('all');
const evaluationNotice = ref('');
const serviceError = ref('');
const serviceErrorStatus = ref<number | undefined>();
const canScoreCandidate = computed(() => hasPermission('candidate.score'));
const canManageStage = computed(() => hasPermission('candidate.stage.manage'));
const canManageInterview = computed(() => hasPermission('interview.manage'));
const serviceErrorTitle = computed(() => {
  if (serviceErrorStatus.value === 403) return '权限不足。';
  if (serviceErrorStatus.value) return '候选人数据加载失败。';
  return '无法连接后端服务。';
});

const weightDimensions = [
  { key: 'project_experience', label: '项目经历' },
  { key: 'skill_match', label: '技能匹配' },
  { key: 'education', label: '教育背景' },
  { key: 'work_experience', label: '工作经验' },
  { key: 'overall_quality', label: '综合素质' },
] as const;

const defaultWeights: Record<WeightKey, number> = {
  project_experience: 25,
  skill_match: 30,
  education: 10,
  work_experience: 20,
  overall_quality: 15,
};

const weights = reactive<Record<WeightKey, number>>({ ...defaultWeights });
const isEmpty = computed(() => candidates.value.length === 0);

const visibleCandidates = computed(() => {
  let list = highMatchOnly.value
    ? candidates.value.filter((item) => item.match !== null && item.match >= 90)
    : [...candidates.value];
  if (selectedJobId.value !== null) {
    list = list.filter((item) => item.jobId === selectedJobId.value);
  }
  if (filterMode.value === 'smart') {
    return list.sort((a, b) => (b.match ?? -1) + (computedScore(b) ?? -1) - ((a.match ?? -1) + (computedScore(a) ?? -1)));
  }
  if (filterMode.value === 'score') {
    return list.sort((a, b) => (computedScore(b) ?? -1) - (computedScore(a) ?? -1));
  }
  return list;
});

const summaryCards = computed(() => [
  { label: '当前候选人', value: String(visibleCandidates.value.length), icon: 'groups' },
  { label: '高匹配候选人', value: String(visibleCandidates.value.filter((item) => item.match !== null && item.match >= 90).length), icon: 'verified' },
  { label: '需复核风险', value: String(visibleCandidates.value.filter((item) => item.riskLevel !== 'low').length), icon: 'warning' },
]);

const selectedCandidate = computed(() => visibleCandidates.value.find((item) => item.id === selectedId.value) ?? visibleCandidates.value[0]);
const nextStageOptions = computed(() => {
  const stage = selectedCandidate.value?.stageCode;
  const map: Partial<Record<PipelineStage, { value: PipelineStage; label: string }[]>> = {
    APPLIED: [{ value: 'AI_SCREENED', label: '推进至初筛通过' }, { value: 'REJECTED', label: '标记为淘汰' }],
    AI_SCREENED: [{ value: 'INTERVIEW_PENDING', label: '推进至待约面' }, { value: 'REJECTED', label: '标记为淘汰' }],
    INTERVIEW_PENDING: [{ value: 'INTERVIEWING', label: '推进至面试中' }, { value: 'REJECTED', label: '标记为淘汰' }],
    INTERVIEWING: [{ value: 'DECISION_PENDING', label: '推进至待决策' }, { value: 'REJECTED', label: '标记为淘汰' }],
    DECISION_PENDING: [{ value: 'OFFERED', label: '推进至已发 Offer' }, { value: 'REJECTED', label: '标记为淘汰' }],
    OFFERED: [{ value: 'HIRED', label: '推进至已入职' }, { value: 'REJECTED', label: '标记为淘汰' }],
  };
  return map[stage ?? 'APPLIED'] ?? [];
});
const emptyFilterMessage = computed(() => (
  highMatchOnly.value
    ? '当前筛选无候选人，可取消“只看高匹配候选人”后查看其他候选人。'
    : '当前岗位暂无候选人，可选择“全部岗位”或其他岗位。'
));

watch(selectedJobId, () => {
  selectedId.value = visibleCandidates.value[0]?.id ?? 0;
});

watch(selectedCandidate, () => {
  targetStage.value = nextStageOptions.value[0]?.value ?? '';
}, { immediate: true });

const filterHint = computed(() => {
  if (highMatchOnly.value) return '当前仅展示岗位匹配度 90% 及以上候选人。';
  if (filterMode.value === 'score') return '当前按 AI 评分从高到低排列。';
  if (filterMode.value === 'smart') return '当前综合评分、匹配度和风险标签进行优先级排序。';
  return '调整下方权重后，选择候选人重新评估即可保存新的评分结果。';
});

onMounted(loadCandidatePool);

const viewingResume = ref(false);

async function viewResume(applicationId: number, name: string) {
  if (viewingResume.value) return;
  viewingResume.value = true;
  try {
    const response = await apiClient.get(`/recruitment/applications/${applicationId}/resume`, {
      responseType: 'blob'
    });
    const headers = response.headers || {};
    const contentType = String(headers['content-type'] || '').toLowerCase();
    const type = contentType.includes('text/plain') ? 'text/plain; charset=utf-8' : 'application/pdf';
    const blob = new Blob([response.data], { type });
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
  } catch (error) {
    emit('show-toast', error instanceof Error ? error.message : '打开简历失败，简历文件可能不存在。');
  } finally {
    viewingResume.value = false;
  }
}

function openResumeFilePicker() {
  if (!importing.value) resumeFileInput.value?.click();
}

async function handleResumeFiles(event: Event) {
  const input = event.target as HTMLInputElement;
  const files = Array.from(input.files ?? []);
  if (!files.length) return;
  if (files.some((file) => !file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf')) {
    emit('show-toast', '仅支持选择 PDF 简历文件。');
    input.value = '';
    return;
  }
  importing.value = true;
  try {
    const result = await importCandidateResumes(files);
    emit('show-toast', `成功导入 ${result.imported_count} 人，跳过重复 ${result.duplicate_count} 人，失败 ${result.failed_count} 份。`);
    const failures = result.items.filter((item) => item.status === 'FAILED');
    if (failures.length) {
      emit('show-toast', failures.map((item) => `${item.filename}：${item.message}`).join('；'));
    }
    const firstImported = result.items.find((item) => item.status === 'IMPORTED');
    if (firstImported?.application_id) {
      await loadCandidatePool(firstImported.application_id);
    }
  } catch (error) {
    emit('show-toast', error instanceof Error ? error.message : '简历导入失败。');
  } finally {
    importing.value = false;
    input.value = '';
  }
}

async function loadCandidatePool(preferredApplicationId?: number) {
  loading.value = true;
  evaluationNotice.value = '';
  serviceError.value = '';
  permissionDenied.value = false;
  serviceErrorStatus.value = undefined;
  try {
    await checkBackendHealth();
    const [jobRows, candidateRows, applicationRows] = await Promise.all([
      fetchJobs(),
      fetchCandidates(),
      fetchApplications()
    ]);
    jobs.value = Array.isArray(jobRows) ? jobRows : [];
    selectedJobId.value = null;
    const mapped = mapBackendCandidates(candidateRows, applicationRows);
    candidates.value = mapped;
    selectedId.value = mapped.find((item) => item.applicationId === preferredApplicationId)?.id
      ?? mapped[0]?.id
      ?? 0;
  } catch (error) {
    if (error instanceof ApiClientError && error.status === 403) {
      permissionDenied.value = true;
      candidates.value = [];
      return;
    }
    serviceErrorStatus.value = error instanceof ApiClientError ? error.status : undefined;
    serviceError.value = error instanceof Error ? error.message : '网络连接失败，服务端未响应。';
    candidates.value = [];
  } finally {
    loading.value = false;
  }
}

function mapBackendCandidates(apiCandidates: ApiCandidate[], applications: CandidateApplicationListItem[]): Candidate[] {
  const candidateMap = new Map(apiCandidates.map((item) => [item.id, item]));
  if (!applications.length) {
    return [];
  }
  return applications.map((application) => {
    const candidate = candidateMap.get(Number(application.candidate_id));
    const score = typeof application.score_total === 'number' ? application.score_total : null;
    return fromApiCandidate(
      candidate,
      Number(application.id),
      String(application.job_title || '待匹配岗位'),
      stageLabel(String(application.current_stage || 'APPLIED')),
      score,
      application.score_breakdown || {},
      Number(application.job_id || 0),
      application.current_stage
    );
  });
}

function fromApiCandidate(
  candidate: ApiCandidate | undefined,
  applicationId: number,
  role: string,
  stage: string,
  score: number | null,
  scoreBreakdown: Record<string, unknown>,
  jobId: number,
  stageCode: PipelineStage = 'APPLIED',
): Candidate {
  const safeScore = score === null ? null : Math.round(score);
  const storedMatch = Number(scoreBreakdown.match_score);
  const match = Number.isFinite(storedMatch) ? Math.round(storedMatch) : safeScore;
  return {
    id: applicationId,
    applicationId,
    jobId,
    name: candidate?.full_name ?? '未命名候选人',
    role,
    stage,
    stageCode,
    aiScore: safeScore,
    match,
    riskLabel: safeScore === null ? '待评估' : safeScore >= 85 ? '低风险' : safeScore >= 70 ? '需复核' : '高风险',
    riskLevel: safeScore === null ? 'medium' : safeScore >= 85 ? 'low' : safeScore >= 70 ? 'medium' : 'high',
    recommendedAction: safeScore === null ? '点击查看评估' : safeScore >= 85 ? '优先安排面试' : safeScore >= 70 ? '进入初筛复核' : '补充材料后评估',
    location: '待确认',
    availableIn: candidate?.available_from ? `${candidate.available_from} 可到岗` : '到岗时间待确认',
    reason: '已读取候选人申请信息，可点击查看评估获取后端评分依据。',
    skillMatch: (candidate?.skills ?? []).length ? `技能包含：${candidate?.skills.join('、')}` : '技能信息待补充。',
    experienceMatch: `候选人经验约 ${Math.round((candidate?.experience_months ?? 0) / 12)} 年。`,
    educationMatch: '学历信息将在评估中作为补充参考。',
    riskDetail: safeScore === null ? '尚未执行岗位评分。' : safeScore >= 85 ? '未发现明显风险。' : '建议结合简历细节进一步复核。',
    interviewAdvice: '建议根据岗位关键能力设置结构化面试问题。',
    dimScores: {
      project_experience: Number(scoreBreakdown.project ?? 0),
      skill_match: Number(scoreBreakdown.skill ?? match ?? 0),
      education: Number(scoreBreakdown.education ?? 0),
      work_experience: Number(scoreBreakdown.experience ?? 0),
      overall_quality: Number(scoreBreakdown.risk ?? safeScore ?? 0),
    },
  };
}

function computedScore(candidate: Candidate): number | null {
  // The sliders are an interactive preview. Recalculate from the persisted
  // dimension scores immediately, while the evaluation action persists the
  // same weights and result through the API.
  if (candidate.aiScore === null) return null;
  const dimensions: Record<WeightKey, number> = {
    project_experience: candidate.dimScores.project_experience ?? 0,
    skill_match: candidate.dimScores.skill_match ?? 0,
    education: candidate.dimScores.education ?? 0,
    work_experience: candidate.dimScores.work_experience ?? 0,
    overall_quality: candidate.dimScores.overall_quality ?? 0,
  };
  const totalWeight = Object.values(weights).reduce((sum, value) => sum + value, 0);
  if (totalWeight <= 0) return candidate.aiScore;
  const weighted = (Object.keys(dimensions) as WeightKey[]).reduce(
    (sum, key) => sum + dimensions[key] * weights[key],
    0,
  ) / totalWeight;
  return Math.round(weighted * 10) / 10;
}

function formatScore(score: number | null): string {
  if (score === null) return '--';
  return score.toFixed(1);
}

function getDimensionScore(candidateId: number, dimKey: WeightKey): number {
  return candidates.value.find((item) => item.id === candidateId)?.dimScores[dimKey] ?? 0;
}

function updateWeight(key: WeightKey, value: number) {
  weights[key] = value;
  emit('show-toast', `${weightDimensions.find((item) => item.key === key)?.label} 权重已调整为 ${value}%。`);
}

function resetWeights() {
  Object.assign(weights, defaultWeights);
  emit('show-toast', '权重已恢复为默认值。');
}

function applySmartFilter() {
  filterMode.value = 'smart';
  highMatchOnly.value = false;
  selectedId.value = visibleCandidates.value[0]?.id ?? 0;
  emit('show-toast', '已按岗位匹配度和风险标签完成智能筛选。');
}

function sortByScore() {
  filterMode.value = 'score';
  selectedId.value = visibleCandidates.value[0]?.id ?? candidates.value[0]?.id ?? 0;
  emit('show-toast', '候选人已按 AI 评分降序排列。');
}

function toggleHighMatch() {
  highMatchOnly.value = !highMatchOnly.value;
  selectedId.value = visibleCandidates.value[0]?.id ?? 0;
  emit(
    'show-toast',
    highMatchOnly.value && visibleCandidates.value.length === 0
      ? '当前筛选无候选人，可取消高匹配筛选。'
      : highMatchOnly.value ? '已切换为只看高匹配候选人。' : '已恢复查看全部候选人。',
  );
}

function formatJobLabel(job: ApiJob): string {
  const title = String(job.title || '').trim() || '未命名岗位';
  const code = String(job.job_code || '').trim();
  const department = String(job.department || '').trim();
  const details = [code, department].filter(Boolean).join(' · ');
  return details ? `${title}（${details}）` : title;
}

async function selectCandidate(candidate: Candidate) {
  selectedId.value = candidate.id;
  try {
    const detail = await fetchApplication(candidate.applicationId);
    applyApplicationDetail(candidate, detail.application);
    evaluationNotice.value = '';
    emit('show-toast', `已打开 ${candidate.name} 的综合评估。`);
  } catch (error) {
    evaluationNotice.value = error instanceof Error ? error.message : '候选人详情暂时无法获取。';
    emit('show-toast', evaluationNotice.value);
  }
}

async function refreshEvaluation(candidate: Candidate) {
  if (!candidate.applicationId || scoring.value) return;
  const weightValues = Object.values(weights);
  if (weightValues.some((value) => !Number.isFinite(value) || value < 0) || weightValues.reduce((sum, value) => sum + value, 0) <= 0) {
    evaluationNotice.value = '评分权重必须是非负数字，且总和必须大于 0。';
    emit('show-toast', evaluationNotice.value);
    return;
  }
  scoring.value = true;
  try {
    const result = await scoreCandidate(candidate.applicationId, { weights: buildScoreWeights() });
    if (result.status === 'algorithm_not_ready') {
      throw new Error(result.message || '智能评估服务暂不可用。');
    }
    applyScoreResult(candidate, result);
    await loadCandidatePool(candidate.applicationId);
    evaluationNotice.value = '';
    emit('show-toast', '已刷新候选人智能评估结果。');
  } catch (error) {
    evaluationNotice.value = error instanceof Error ? error.message : '智能评估暂时无法获取。';
    emit('show-toast', evaluationNotice.value);
  } finally {
    scoring.value = false;
  }
}

async function advanceSelectedStage() {
  const candidate = selectedCandidate.value;
  if (!candidate || !targetStage.value || advancing.value) return;
  advancing.value = true;
  try {
    await advanceCandidateStage(candidate.applicationId, {
      to_stage: targetStage.value,
      note: stageNote.value || undefined,
    });
    await loadCandidatePool(candidate.applicationId);
    stageNote.value = '';
    evaluationNotice.value = '候选人阶段已保存。';
    emit('show-toast', '候选人阶段已保存。');
  } catch (error) {
    const message = error instanceof Error ? error.message : '候选人阶段保存失败。';
    evaluationNotice.value = message;
    emit('show-toast', message);
  } finally {
    advancing.value = false;
  }
}

function buildScoreWeights() {
  return {
    skill: weights.skill_match / 100,
    experience: weights.work_experience / 100,
    education: weights.education / 100,
    project: weights.project_experience / 100,
    risk: weights.overall_quality / 100,
  };
}

function applyScoreResult(candidate: Candidate, result: CandidateScoreResponse) {
  const target = candidates.value.find((item) => item.id === candidate.id);
  if (!target) return;
  const total = Math.round(Number(result.score_total ?? result.overall_score ?? target.aiScore ?? 0));
  const match = Math.round(Number(result.match_score ?? result.match_rate ?? target.match ?? total));
  target.aiScore = total;
  target.match = match;
  target.skillMatch = result.skill_match || target.skillMatch;
  target.experienceMatch = result.experience_match || target.experienceMatch;
  target.educationMatch = result.education_match || target.educationMatch;
  target.riskDetail = result.risk_prompt || target.riskDetail;
  target.riskLabel = result.risk_tags?.[0] || (match >= 85 ? '低风险' : '需复核');
  target.riskLevel = match >= 85 ? 'low' : match >= 70 ? 'medium' : 'high';
  target.recommendedAction = result.recommended_action || target.recommendedAction;
  target.reason = result.scoring_basis?.join(' ') || target.reason;
  target.interviewAdvice = result.recommended_action || target.interviewAdvice;
  target.dimScores = {
    project_experience: Math.round(Number(result.score_breakdown?.project ?? target.dimScores.project_experience)),
    skill_match: Math.round(Number(result.score_breakdown?.skill ?? target.dimScores.skill_match)),
    education: Math.round(Number(result.score_breakdown?.education ?? target.dimScores.education)),
    work_experience: Math.round(Number(result.score_breakdown?.experience ?? target.dimScores.work_experience)),
    overall_quality: Math.round(Number(result.score_breakdown?.risk ?? target.dimScores.overall_quality)),
  };
}

function applyApplicationDetail(candidate: Candidate, application: CandidateApplicationListItem) {
  const target = candidates.value.find((item) => item.id === candidate.id);
  if (!target) return;
  target.stageCode = application.current_stage;
  target.stage = stageLabel(application.current_stage);
  target.aiScore = application.score_total === null ? null : Math.round(Number(application.score_total));
  const breakdown = application.score_breakdown || {};
  const match = Number(breakdown.match_score);
  target.match = Number.isFinite(match) ? Math.round(match) : target.aiScore;
  target.dimScores = {
    project_experience: Number(breakdown.project ?? 0),
    skill_match: Number(breakdown.skill ?? 0),
    education: Number(breakdown.education ?? 0),
    work_experience: Number(breakdown.experience ?? 0),
    overall_quality: Number(breakdown.risk ?? 0),
  };
}

function scheduleInterview(candidate: Candidate) {
  emit('show-toast', `正在为 ${candidate.name} 准备面试排期建议。`);
  router.push({ path: '/hr/interviews', query: { application_id: candidate.applicationId } });
}

function stageLabel(stage: string) {
  const map: Record<string, string> = {
    APPLIED: '已投递',
    AI_SCREENED: '初筛通过',
    INTERVIEW_PENDING: '待约面',
    INTERVIEWING: '面试中',
    DECISION_PENDING: '待决策',
    OFFERED: '已发 Offer',
    HIRED: '已入职',
    REJECTED: '已淘汰',
  };
  return map[stage] ?? stage;
}

function stageClass(stage: string) {
  return {
    'tag tag--blue': stage.includes('约面') || stage.includes('初筛') || stage.includes('投递'),
    'tag tag--amber': stage.includes('复核') || stage.includes('决策'),
    'tag tag--green': stage.includes('Offer') || stage.includes('入职'),
  };
}

function riskClass(level: Candidate['riskLevel']) {
  return {
    'tag tag--green': level === 'low',
    'tag tag--amber': level === 'medium',
    'tag tag--red': level === 'high',
  };
}
</script>

<style scoped>
.candidate-pool { display: grid; gap: 22px; }
.candidate-pool__hero, .candidate-pool__summary, .candidate-pool__content, .notice { max-width: 1440px; width: 100%; margin: 0 auto; }
.candidate-pool__hero { display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; }
.candidate-pool__eyebrow { margin: 0 0 8px; color: var(--color-primary); font-size: 13px; font-weight: 800; }
.candidate-pool__hero h2 { margin: 0; color: var(--color-text); font-size: 30px; line-height: 1.15; }
.candidate-pool__hero p { margin: 8px 0 0; color: var(--color-muted); }
.candidate-pool__actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; }
.notice { padding: 12px 14px; border: 1px solid var(--color-node-skipped-border); border-radius: var(--radius-md); background: var(--color-status-warning-bg); color: var(--color-status-warning-text); font-weight: 700; }
.service-error { max-width: 1440px; width: 100%; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 16px; border: 1px solid var(--color-node-failed-border); border-radius: var(--radius-md); background: var(--color-status-error-bg); color: var(--color-status-error-text); }
.service-error strong, .service-error span { display: block; }
.service-error span { margin-top: 3px; color: var(--color-status-error-text); font-size: 13px; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 7px; min-height: 40px; padding: 0 14px; border: 1px solid var(--color-line); border-radius: var(--radius-sm); background: var(--color-surface); color: var(--color-text); font-weight: 800; cursor: pointer; transition: 0.2s ease; }
.btn:hover, .btn--active { border-color: rgba(36,85,245,0.35); background: var(--color-primary-soft); color: var(--color-primary); }
.btn--primary { border-color: var(--color-primary); background: var(--color-primary); color: #fff; }
.btn--primary:hover { background: #173fd1; color: #fff; }
.btn:disabled { opacity: 0.55; cursor: wait; }
.candidate-pool__summary { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.metric-card { display: flex; align-items: center; gap: 12px; padding: 18px; border: 1px solid var(--color-line); border-radius: var(--radius-md); background: var(--color-surface); box-shadow: var(--shadow-card); }
.metric-card > span { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 12px; background: var(--color-primary-soft); color: var(--color-primary); }
.metric-card strong, .metric-card small { display: block; }
.metric-card strong { color: var(--color-text); font-size: 26px; }
.metric-card small { color: var(--color-muted); font-weight: 700; }
.candidate-pool__content { display: grid; grid-template-columns: minmax(0, 1.7fr) minmax(360px, 0.9fr); gap: 18px; align-items: start; }
.candidate-pool__left { display: flex; flex-direction: column; gap: 18px; }
.candidate-table-card, .candidate-detail-card { border: 1px solid var(--color-line); border-radius: var(--radius-md); background: var(--color-surface); box-shadow: var(--shadow-card); }
.candidate-table-card { overflow: hidden; }
.candidate-table-card__header { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 18px 20px; border-bottom: 1px solid var(--color-line); }
.candidate-table-card__header h3, .candidate-detail-card__header h3 { margin: 0; color: var(--color-text); }
.candidate-table-card__header p, .candidate-detail-card__header p, .candidate-detail-card__header small { margin: 4px 0 0; color: var(--color-muted); }
.candidate-table-card__header > span { padding: 6px 10px; border-radius: 999px; background: var(--color-surface-soft); color: var(--color-muted); font-weight: 800; }
.candidate-table { display: grid; }
.candidate-row { display: grid; grid-template-columns: minmax(180px, 1.4fr) minmax(150px, 1fr) 100px 90px minmax(140px, 1fr); gap: 12px; align-items: center; width: 100%; padding: 16px 20px; border: 0; border-bottom: 1px solid var(--color-line); background: transparent; color: var(--color-text); text-align: left; cursor: pointer; transition: 0.18s ease; }
.candidate-row:hover, .candidate-row--selected { background: #f7f9ff; }
.candidate-row:last-child { border-bottom: 0; }
.candidate-row__name strong, .candidate-row__name small, .candidate-row__action strong { display: block; }
.candidate-row__name small { margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.candidate-row .score { color: var(--color-primary); font-size: 22px; font-weight: 900; }
.candidate-row__action strong { margin-bottom: 5px; font-size: 13px; }
.link-button { padding: 0; border: 0; background: transparent; color: var(--color-primary); font-size: 12px; font-weight: 800; cursor: pointer; }
.match-bar { display: block; height: 8px; margin-bottom: 5px; overflow: hidden; border-radius: 999px; background: var(--color-surface-soft); }
.match-bar i { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #2455f5, #16a34a); }
.tag { display: inline-flex; align-items: center; min-height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-style: normal; font-weight: 800; }
.tag--blue { background: var(--color-primary-soft); color: #2455f5; }
.tag--green { background: #dcfce7; color: #15803d; }
.tag--amber { background: var(--color-status-warning-bg); color: var(--color-status-warning-text); }
.tag--red { background: var(--color-status-error-bg); color: var(--color-status-error-text); }
.candidate-detail-card { position: sticky; top: 92px; display: grid; gap: 14px; padding: 16px; }
.candidate-detail-card__header { display: flex; justify-content: space-between; gap: 16px; padding-bottom: 16px; border-bottom: 1px solid var(--color-line); }
.candidate-detail-card__score { display: grid; width: 92px; height: 92px; place-items: center; align-content: center; padding: 12px; border-radius: 16px; background: var(--color-primary-soft); color: var(--color-primary); box-sizing: border-box; flex-shrink: 0; }
.candidate-detail-card__score strong { font-size: 32px; line-height: 1; }
.candidate-detail-card__score span { margin-top: 5px; font-size: 12px; font-weight: 800; }
.score-breakdown { padding: 12px; border: 1px solid var(--color-line); border-radius: 12px; background: var(--color-surface-soft); }
.score-breakdown h4 { margin: 0 0 8px; font-size: 13px; font-weight: 800; color: var(--color-muted); }
.score-breakdown__row { display: flex; align-items: center; gap: 6px; margin-bottom: 5px; }
.score-breakdown__label { font-size: 12px; color: var(--color-muted); white-space: nowrap; width: 56px; font-weight: 600; }
.score-breakdown__bar-bg { flex: 1; height: 6px; border-radius: 3px; background: var(--color-line); overflow: hidden; }
.score-breakdown__bar { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.score-breakdown__val { min-width: 28px; text-align: right; color: var(--color-primary); font-weight: 800; }
.detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.detail-grid article, .interview-advice { padding: 14px; border: 1px solid var(--color-line); border-radius: 14px; background: var(--color-surface-soft); }
.detail-grid__wide { grid-column: 1 / -1; }
.detail-grid article span, .interview-advice span { color: var(--color-primary); }
.detail-grid article strong, .interview-advice strong { display: block; margin-top: 6px; color: var(--color-text); }
.detail-grid article p, .interview-advice p { margin: 7px 0 0; color: var(--color-muted); font-size: 13px; line-height: 1.55; }
.interview-advice > div { display: flex; align-items: center; gap: 8px; }
.interview-advice strong { margin-top: 0; }
.candidate-detail-card__footer { display: flex; flex-wrap: wrap; gap: 10px; }
.stage-management { display: grid; gap: 10px; padding: 12px; border: 1px solid var(--color-line); border-radius: 12px; background: var(--color-surface-soft); }
.stage-management p { margin: 0; color: var(--color-muted); font-size: 13px; }
.stage-select { min-height: 40px; max-width: 180px; border: 1px solid var(--color-line); border-radius: var(--radius-sm); background: var(--color-surface); color: var(--color-text); padding: 0 10px; font-weight: 700; }
.stage-note { min-height: 40px; padding: 0 10px; border: 1px solid var(--color-line); border-radius: var(--radius-sm); background: var(--color-surface); color: var(--color-text); }
.terminal-stage { color: var(--color-muted); font-size: 13px; }
.weight-sandbox { max-width: 1440px; margin: 0 auto 22px; padding: 20px 24px; border: 1px solid var(--color-line); border-radius: var(--radius-md); background: var(--color-surface); box-shadow: var(--shadow-card); }
.weight-sandbox--inline { max-width: none; margin: 0; }
.weight-sandbox__header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.weight-sandbox__header h3, .weight-sandbox__reset { display: flex; align-items: center; gap: 8px; }
.weight-sandbox__header h3 { margin: 0; font-size: 16px; font-weight: 800; color: var(--color-text); }
.weight-sandbox__reset { padding: 6px 14px; border: 1px solid var(--color-line); border-radius: var(--radius-sm); background: var(--color-surface); color: var(--color-muted); font-size: 12px; font-weight: 700; cursor: pointer; }
.weight-sandbox__sliders { display: flex; flex-direction: column; gap: 0; }
.weight-slider { padding: 14px 0; border-bottom: 1px solid var(--color-line); }
.weight-slider:last-child { border-bottom: 0; padding-bottom: 0; }
.weight-slider:first-child { padding-top: 0; }
.weight-slider__header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.weight-slider__header label { font-size: 14px; font-weight: 700; color: var(--color-text); }
.weight-slider__value { color: var(--color-primary); font-weight: 900; font-size: 14px; }
.weight-slider__input { width: 100%; }
.job-filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
  padding: 12px 18px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}
.job-filter-bar label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-muted);
}
.job-filter-bar label span {
  font-size: 18px;
  color: var(--color-primary);
}
.job-select {
  padding: 8px 12px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 14px;
  font-weight: 600;
  outline: none;
  cursor: pointer;
  min-width: 260px;
  transition: border-color 0.2s ease;
}
.job-select:focus {
  border-color: var(--color-primary);
}
@media (max-width: 1180px) { .candidate-pool__content { grid-template-columns: 1fr; } .candidate-detail-card { position: static; } }
@media (max-width: 860px) { .candidate-pool__hero { align-items: stretch; flex-direction: column; } .candidate-pool__summary, .detail-grid { grid-template-columns: 1fr; } .candidate-row { grid-template-columns: 1fr; } }

/* 深色模式适配 */
[data-theme="dark"] .candidate-row:hover,
[data-theme="dark"] .candidate-row--selected { background: #1e293b; }
[data-theme="dark"] .tag--green { background: #052e16; color: #86efac; }
</style>
