<template>
  <div class="candidate-pool">
    <LoadingState v-if="loading" message="正在加载候选人数据..." detail="正在读取招聘候选人与申请信息" />

    <PermissionDenied
      v-else-if="permissionDenied"
      description="你当前的角色无权访问候选人池，如需协助请联系 HR 管理员。"
    />

    <EmptyState
      v-else-if="isEmpty"
      title="暂无候选人"
      description="当前岗位还没有候选人申请，请先发布岗位或导入简历。"
    />

    <template v-else>
      <section v-if="serviceError" class="service-error">
        <div>
          <strong>服务暂不可用，请确认后端已启动。</strong>
          <span>{{ serviceError }}</span>
        </div>
        <button class="btn" @click="loadCandidatePool">重新加载</button>
      </section>

      <section class="candidate-pool__hero">
        <div>
          <p class="candidate-pool__eyebrow">招聘决策</p>
          <h2>候选人池</h2>
          <p>集中查看候选人评分、岗位匹配度、风险标签与下一步推荐动作。</p>
        </div>
        <div class="candidate-pool__actions">
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
        <div class="candidate-table-card">
          <div class="candidate-table-card__header">
            <div>
              <h3>候选人列表</h3>
              <p>{{ filterHint }}</p>
            </div>
            <span>{{ visibleCandidates.length }} 人</span>
          </div>

          <EmptyState
            v-if="visibleCandidates.length === 0"
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
              <span class="score">{{ computedScore(candidate) ?? '--' }}</span>
              <span v-if="candidate.match !== null">
                <span class="match-bar"><i :style="{ width: `${candidate.match}%` }"></i></span>
                <small>{{ candidate.match }}%</small>
              </span>
              <span v-else class="text-on-surface-variant">待评估</span>
              <span><em :class="riskClass(candidate.riskLevel)">{{ candidate.riskLabel }}</em></span>
              <span class="candidate-row__action">
                <strong>{{ candidate.recommendedAction }}</strong>
                <button class="link-button" @click.stop="selectCandidate(candidate)">查看评估</button>
              </span>
            </button>
          </div>
        </div>

        <aside v-if="selectedCandidate" class="candidate-detail-card">
          <div class="candidate-detail-card__header">
            <div>
              <p>AI 综合评估</p>
              <h3>{{ selectedCandidate.name }}</h3>
              <small>{{ selectedCandidate.role }} · {{ selectedCandidate.stage }}</small>
            </div>
            <div class="candidate-detail-card__score">
              <strong>{{ computedScore(selectedCandidate) ?? '--' }}</strong>
              <span>综合评分</span>
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

          <div class="candidate-detail-card__footer">
            <button class="btn btn--primary" @click="scheduleInterview(selectedCandidate)">
              <span class="material-symbols-outlined">event_available</span>
              安排面试
            </button>
            <button class="btn" :disabled="scoring" @click="refreshEvaluation(selectedCandidate)">
              <span class="material-symbols-outlined">article</span>
              {{ scoring ? '评估中...' : '查看评估依据' }}
            </button>
          </div>
        </aside>

        <section class="weight-sandbox weight-sandbox--inline">
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
import { fetchApplications, fetchCandidates, scoreCandidate, fetchJobs } from '../shared/api/modules/recruitment';
import { checkBackendHealth } from '../shared/api/modules/health';
import { ApiClientError } from '../shared/api/apiClient';
import type { CandidateApplicationListItem } from '../shared/api/modules/recruitment';
import type { Candidate as ApiCandidate, CandidateScoreResponse, Job as ApiJob } from '../shared/api/types';

const router = useRouter();

type Candidate = {
  id: number;
  applicationId: number;
  jobId: number;
  name: string;
  role: string;
  stage: string;
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
const scoring = ref(false);
const permissionDenied = ref(false);
const candidates = ref<Candidate[]>([]);
const jobs = ref<ApiJob[]>([]);
const selectedJobId = ref<number | null>(null);
const selectedId = ref<number>(0);
const highMatchOnly = ref(false);
const filterMode = ref<'all' | 'smart' | 'score'>('all');
const evaluationNotice = ref('');
const serviceError = ref('');

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
const emptyFilterMessage = computed(() => (
  highMatchOnly.value
    ? '当前筛选无候选人，可取消“只看高匹配候选人”后查看其他候选人。'
    : '当前岗位暂无候选人，可选择“全部岗位”或其他岗位。'
));

watch(selectedJobId, () => {
  selectedId.value = visibleCandidates.value[0]?.id ?? 0;
});

const filterHint = computed(() => {
  if (highMatchOnly.value) return '当前仅展示岗位匹配度 90% 及以上候选人。';
  if (filterMode.value === 'score') return '当前按 AI 评分从高到低排列。';
  if (filterMode.value === 'smart') return '当前综合评分、匹配度和风险标签进行优先级排序。';
  return '调整下方权重后，评分和排序将实时更新。';
});

onMounted(loadCandidatePool);

async function loadCandidatePool() {
  loading.value = true;
  evaluationNotice.value = '';
  serviceError.value = '';
  permissionDenied.value = false;
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
  } catch (error) {
    if (error instanceof ApiClientError && error.status === 403) {
      permissionDenied.value = true;
      return;
    }
    serviceError.value = error instanceof Error ? error.message : '网络连接失败，服务端未响应。';
    evaluationNotice.value = '智能评估暂时无法获取，已显示本地评估摘要。';
    useLocalCandidates();
  } finally {
    selectedId.value = visibleCandidates.value[0]?.id ?? 0;
    loading.value = false;
  }
}

function mapBackendCandidates(apiCandidates: ApiCandidate[], applications: CandidateApplicationListItem[]): Candidate[] {
  const candidateMap = new Map(apiCandidates.map((item) => [item.id, item]));
  if (!applications.length) {
    return apiCandidates.map((item) => fromApiCandidate(item, item.id, '待匹配岗位', '待初筛', null, {}, 0));
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
      Number(application.job_id || 0)
    );
  });
}

function fromApiCandidate(
  candidate: ApiCandidate | undefined,
  applicationId: number,
  role: string,
  stage: string,
  score: number | null,
  scoreBreakdown: Record<string, number>,
  jobId: number
): Candidate {
  const safeScore = score === null ? null : Math.round(score);
  const storedMatch = Number(scoreBreakdown.match_score);
  const match = Number.isFinite(storedMatch) ? Math.round(storedMatch) : safeScore;
  return {
    id: candidate?.id ?? applicationId,
    applicationId,
    jobId,
    name: candidate?.full_name ?? '未命名候选人',
    role,
    stage,
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

function useLocalCandidates() {
  candidates.value = [
    createCandidate(1, 1, 'Eleanor Vance', '首席数据科学家', '待约面', 94, 94, '低风险', 'low', '优先安排技术面试'),
    createCandidate(2, 2, 'Michael Chen', '高级前端工程师', '初筛通过', 91, 92, '到岗需确认', 'medium', '补充到岗时间确认'),
    createCandidate(3, 3, 'Sarah Jenkins', '产品经理', '待复核', 87, 86, '薪资偏高', 'medium', '薪资范围预沟通'),
    createCandidate(4, 4, '刘伟', '后端工程师', '简历筛选', 82, 79, '技能缺口', 'high', '补充项目材料'),
  ];
}

function createCandidate(
  id: number,
  applicationId: number,
  name: string,
  role: string,
  stage: string,
  aiScore: number,
  match: number,
  riskLabel: string,
  riskLevel: Candidate['riskLevel'],
  action: string
): Candidate {
  return {
    id,
    applicationId,
    jobId: 1,
    name,
    role,
    stage,
    aiScore,
    match,
    riskLabel,
    riskLevel,
    recommendedAction: action,
    location: id === 1 ? '上海' : id === 2 ? '杭州' : id === 3 ? '北京' : '广州',
    availableIn: id === 1 ? '4 周到岗' : id === 2 ? '6 周到岗' : id === 3 ? '3 周到岗' : '2 周到岗',
    reason: '候选人核心经历与岗位画像具备较好重合，建议结合面试进一步确认业务场景经验。',
    skillMatch: '技能覆盖岗位关键要求，少量专项能力需要在面试中继续验证。',
    experienceMatch: '相关年限满足岗位基础要求，项目复杂度需要结合案例追问。',
    educationMatch: '学历背景满足基础筛选要求，可作为补充参考。',
    riskDetail: riskLevel === 'low' ? '未发现明显风险。' : '存在需要复核的风险项，建议在推进前确认。',
    interviewAdvice: '建议围绕岗位关键能力、项目复盘和协作方式设计结构化问题。',
    dimScores: {
      project_experience: Math.max(55, aiScore - 3),
      skill_match: match,
      education: Math.max(60, aiScore - 6),
      work_experience: Math.max(58, aiScore - 4),
      overall_quality: Math.max(60, aiScore - 2),
    },
  };
}

function computedScore(candidate: Candidate): number | null {
  if (candidate.aiScore === null) return null;
  const totalWeight = weightDimensions.reduce((sum, dim) => sum + weights[dim.key], 0);
  if (!totalWeight) return 0;
  const total = weightDimensions.reduce((sum, dim) => sum + weights[dim.key] * (candidate.dimScores[dim.key] ?? 0), 0);
  return Math.round(total / totalWeight);
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
  emit('show-toast', `已打开 ${candidate.name} 的综合评估。`);
  await refreshEvaluation(candidate);
}

async function refreshEvaluation(candidate: Candidate) {
  if (!candidate.applicationId || scoring.value) return;
  scoring.value = true;
  try {
    const result = await scoreCandidate(candidate.applicationId, { weights: buildScoreWeights() });
    if (result.status === 'algorithm_not_ready') {
      throw new Error('score unavailable');
    }
    applyScoreResult(candidate, result);
    evaluationNotice.value = '';
    emit('show-toast', '已刷新候选人智能评估结果。');
  } catch {
    evaluationNotice.value = '智能评估暂时无法获取，已显示本地评估摘要。';
    emit('show-toast', '智能评估暂时无法获取，已显示本地评估摘要。');
  } finally {
    scoring.value = false;
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

function scheduleInterview(candidate: Candidate) {
  emit('show-toast', `正在为 ${candidate.name} 准备面试排期建议。`);
  setTimeout(() => {
    router.push({ path: '/hr/interviews', query: { applicationId: candidate.applicationId } });
  }, 300);
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
.notice { padding: 12px 14px; border: 1px solid #fde68a; border-radius: var(--radius-md); background: #fffbeb; color: #92400e; font-weight: 700; }
.service-error { max-width: 1440px; width: 100%; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 16px; border: 1px solid #fecaca; border-radius: var(--radius-md); background: #fff7f7; color: #991b1b; }
.service-error strong, .service-error span { display: block; }
.service-error span { margin-top: 3px; color: #b91c1c; font-size: 13px; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 7px; min-height: 40px; padding: 0 14px; border: 1px solid var(--color-line); border-radius: var(--radius-sm); background: #fff; color: var(--color-text); font-weight: 800; cursor: pointer; transition: 0.2s ease; }
.btn:hover, .btn--active { border-color: rgba(36,85,245,0.35); background: var(--color-primary-soft); color: var(--color-primary); }
.btn--primary { border-color: var(--color-primary); background: var(--color-primary); color: #fff; }
.btn--primary:hover { background: #173fd1; color: #fff; }
.btn:disabled { opacity: 0.55; cursor: wait; }
.candidate-pool__summary { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.metric-card { display: flex; align-items: center; gap: 12px; padding: 18px; border: 1px solid var(--color-line); border-radius: var(--radius-md); background: #fff; box-shadow: var(--shadow-card); }
.metric-card > span { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 12px; background: var(--color-primary-soft); color: var(--color-primary); }
.metric-card strong, .metric-card small { display: block; }
.metric-card strong { color: var(--color-text); font-size: 26px; }
.metric-card small { color: var(--color-muted); font-weight: 700; }
.candidate-pool__content { display: grid; grid-template-columns: minmax(0, 1.7fr) minmax(360px, 0.9fr); gap: 18px; align-items: start; }
.candidate-table-card, .candidate-detail-card { border: 1px solid var(--color-line); border-radius: var(--radius-md); background: #fff; box-shadow: var(--shadow-card); }
.candidate-table-card { overflow: hidden; }
.candidate-table-card__header { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 18px 20px; border-bottom: 1px solid var(--color-line); }
.candidate-table-card__header h3, .candidate-detail-card__header h3 { margin: 0; color: var(--color-text); }
.candidate-table-card__header p, .candidate-detail-card__header p, .candidate-detail-card__header small { margin: 4px 0 0; color: var(--color-muted); }
.candidate-table-card__header > span { padding: 6px 10px; border-radius: 999px; background: var(--color-surface-soft); color: var(--color-muted); font-weight: 800; }
.candidate-table { display: grid; }
.candidate-row { display: grid; grid-template-columns: minmax(160px,1.3fr) minmax(130px,1fr) 92px 78px minmax(120px,0.9fr) 112px minmax(150px,1fr); gap: 12px; align-items: center; width: 100%; padding: 16px 20px; border: 0; border-bottom: 1px solid var(--color-line); background: transparent; color: var(--color-text); text-align: left; cursor: pointer; transition: 0.18s ease; }
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
.tag--blue { background: #eaf0ff; color: #2455f5; }
.tag--green { background: #dcfce7; color: #15803d; }
.tag--amber { background: #fff7ed; color: #c2410c; }
.tag--red { background: #fee2e2; color: #b91c1c; }
.candidate-detail-card { position: sticky; top: 92px; display: grid; gap: 14px; padding: 16px; }
.candidate-detail-card__header { display: flex; justify-content: space-between; gap: 16px; padding-bottom: 16px; border-bottom: 1px solid var(--color-line); }
.candidate-detail-card__score { display: grid; min-width: 92px; place-items: center; padding: 12px; border-radius: 16px; background: var(--color-primary-soft); color: var(--color-primary); }
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
.weight-sandbox { max-width: 1440px; margin: 0 auto 22px; padding: 20px 24px; border: 1px solid var(--color-primary); border-radius: var(--radius-md); background: linear-gradient(135deg, rgba(36,85,245,0.03), rgba(36,85,245,0.01)); box-shadow: 0 2px 12px rgba(36,85,245,0.06); }
.weight-sandbox--inline { grid-column: 1 / -1; max-width: none; margin: 0; }
.weight-sandbox__header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.weight-sandbox__header h3, .weight-sandbox__reset { display: flex; align-items: center; gap: 8px; }
.weight-sandbox__header h3 { margin: 0; font-size: 16px; font-weight: 800; color: var(--color-primary); }
.weight-sandbox__reset { padding: 6px 14px; border: 1px solid var(--color-line); border-radius: var(--radius-sm); background: #fff; color: var(--color-muted); font-size: 12px; font-weight: 700; cursor: pointer; }
.weight-sandbox__sliders { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 18px; }
.weight-slider__header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.weight-slider__header label { font-size: 13px; font-weight: 700; color: var(--color-muted); }
.weight-slider__value { color: var(--color-primary); font-weight: 900; }
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
  background: #fff;
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
  background: #fff;
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
@media (max-width: 1180px) { .candidate-pool__content { grid-template-columns: 1fr; } .candidate-detail-card { position: static; } .weight-sandbox__sliders { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 860px) { .candidate-pool__hero { align-items: stretch; flex-direction: column; } .candidate-pool__summary, .detail-grid { grid-template-columns: 1fr; } .candidate-row { grid-template-columns: 1fr; } }
</style>
