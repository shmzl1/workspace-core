<template>
  <div class="candidate-pool">
    <!-- 加载态 -->
    <LoadingState
      v-if="loading"
      message="正在加载候选人数据…"
      detail="从招聘服务获取候选人信息"
    />

    <!-- 权限拒绝 -->
    <PermissionDenied
      v-else-if="permissionDenied"
      description="你当前的角色无权访问候选人池，如需协助请联系 HR 管理员。"
    />

    <!-- 错误态 -->
    <ErrorState
      v-else-if="error"
      :message="error"
      retry-label="重新加载"
      @retry="retry"
    />

    <!-- 空态 -->
    <EmptyState
      v-else-if="isEmpty"
      title="暂无候选人"
      description="当前岗位还没有候选人申请，请先发布岗位或导入简历。"
    />

    <!-- 正常内容 -->
    <template v-else>
      <!-- Hero -->
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
            只看高匹配
          </button>
        </div>
      </section>

      <!-- Summary -->
      <section class="candidate-pool__summary">
        <article v-for="item in summaryCards" :key="item.label" class="metric-card">
          <span class="material-symbols-outlined">{{ item.icon }}</span>
          <div>
            <strong>{{ item.value }}</strong>
            <small>{{ item.label }}</small>
          </div>
        </article>
      </section>

      <!-- Main content -->
      <section class="candidate-pool__content">
        <!-- 候选人表格 -->
        <div class="candidate-table-card">
          <div class="candidate-table-card__header">
            <div>
              <h3>候选人列表</h3>
              <p>{{ filterHint }}</p>
            </div>
            <span>{{ visibleCandidates.length }} 人</span>
          </div>

          <div class="candidate-table">
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
              <span>
                <em :class="stageClass(candidate.stage)">{{ candidate.stage }}</em>
              </span>
              <span class="score">{{ computedScore(candidate) }}</span>
              <span>
                <span class="match-bar">
                  <i :style="{ width: `${candidate.match}%` }"></i>
                </span>
                <small>{{ candidate.match }}%</small>
              </span>
              <span>
                <em :class="riskClass(candidate.riskLevel)">{{ candidate.riskLabel }}</em>
              </span>
              <span class="candidate-row__action">
                <strong>{{ candidate.recommendedAction }}</strong>
                <button class="link-button" @click.stop="selectCandidate(candidate)">查看评估</button>
              </span>
            </button>
          </div>
        </div>

        <!-- 右侧详情面板 -->
        <aside class="candidate-detail-card">
          <div class="candidate-detail-card__header">
            <div>
              <p>AI 综合评估</p>
              <h3>{{ selectedCandidate.name }}</h3>
              <small>{{ selectedCandidate.role }} · {{ selectedCandidate.stage }}</small>
            </div>
            <div class="candidate-detail-card__score">
              <strong>{{ computedScore(selectedCandidate) }}</strong>
              <span>综合评分</span>
            </div>
          </div>

          <!-- 评分维度分解 -->
          <div class="score-breakdown">
            <h4>评分维度分解</h4>
            <div v-for="dim in weightDimensions" :key="dim.key" class="score-breakdown__row">
              <span class="score-breakdown__label">{{ dim.label }}</span>
              <span class="score-breakdown__bar-bg">
                <span
                  class="score-breakdown__bar"
                  :style="{ width: `${getDimensionScore(selectedCandidate.id, dim.key)}%` }"
                ></span>
              </span>
              <span class="score-breakdown__val">
                {{ getDimensionScore(selectedCandidate.id, dim.key) }}
              </span>
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
            <button class="btn" @click="emit('show-toast', '评估依据已展开。')">
              <span class="material-symbols-outlined">article</span>
              查看评估依据
            </button>
          </div>
        </aside>

        <!-- ── 权重调整沙盘（嵌入左侧列空白区，grid row 2）── -->
        <section class="weight-sandbox weight-sandbox--inline">
          <div class="weight-sandbox__header">
            <h3>
              <span class="material-symbols-outlined">tune</span>
              评分维度权重调整
            </h3>
            <button class="weight-sandbox__reset" @click="resetWeights">
              <span class="material-symbols-outlined" style="font-size:14px">restart_alt</span>
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
                :min="0"
                :max="100"
                :value="weights[dim.key]"
                class="weight-slider__input"
                @input="(e: Event) => updateWeight(dim.key, Number((e.target as HTMLInputElement).value))"
              />
            </div>
          </div>
          <p class="weight-sandbox__hint">
            加权总分 = (项目经历×{{ weights.project_experience }} + 技能匹配×{{ weights.skill_match }} + 教育背景×{{ weights.education }} + 工作经验×{{ weights.work_experience }} + 综合素养×{{ weights.overall_quality }}) ÷ {{ weights.project_experience + weights.skill_match + weights.education + weights.work_experience + weights.overall_quality }}
          </p>
        </section>
      </section>

    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import ErrorState from '../shared/components/feedback/ErrorState.vue';
import EmptyState from '../shared/components/feedback/EmptyState.vue';
import PermissionDenied from '../shared/components/feedback/PermissionDenied.vue';

// ── 类型 ─────────────────────────────────────
type Candidate = {
  id: number;
  name: string;
  role: string;
  stage: string;
  aiScore: number;
  match: number;
  riskLabel: string;
  riskLevel: 'low' | 'medium' | 'high';
  recommendedAction: string;
  location: string;
  availableIn: string;
  reason: string;
  skillMatch: string;
  experienceMatch: string;
  riskDetail: string;
  interviewAdvice: string;
  /** 各维度分项得分 (0-100) */
  dimScores: Record<string, number>;
};

const emit = defineEmits<{
  navigate: [view: string];
  'show-toast': [message: string];
}>();

// ── 状态 ─────────────────────────────────────
const loading = ref(true);
const error = ref<string | null>(null);
const permissionDenied = ref(false);
const isEmpty = computed(() => candidates.value.length === 0);

// ── 评分维度定义 ──────────────────────────────
const weightDimensions = [
  { key: 'project_experience', label: '项目经历' },
  { key: 'skill_match', label: '技能匹配' },
  { key: 'education', label: '教育背景' },
  { key: 'work_experience', label: '工作经验' },
  { key: 'overall_quality', label: '综合素养' },
] as const;

const defaultWeights: Record<string, number> = {
  project_experience: 25,
  skill_match: 30,
  education: 10,
  work_experience: 20,
  overall_quality: 15,
};

const weights = reactive({ ...defaultWeights });

// ── 候选人数据 ───────────────────────────────
const candidates = ref<Candidate[]>([]);
const selectedId = ref<number>(0);
const highMatchOnly = ref(false);
const filterMode = ref<'all' | 'smart' | 'score'>('all');

// ── 初始化 ───────────────────────────────────
function initData() {
  candidates.value = [
    {
      id: 1, name: 'Eleanor Vance', role: '首席数据科学家', stage: '待约面',
      aiScore: 94, match: 94, riskLabel: '低风险', riskLevel: 'low',
      recommendedAction: '优先安排技术终面', location: '上海', availableIn: '4 周到岗',
      reason: '机器学习、知识检索与团队协作经验完整，核心能力覆盖岗位画像中的关键要求。',
      skillMatch: 'Python、模型评估、知识检索与数据治理匹配度高，云平台经验可迁移。',
      experienceMatch: '8 年相关经验，具备跨团队项目交付与算法产品化经验。',
      riskDetail: '薪资期望偏高，需要在终面前确认预算区间。',
      interviewAdvice: '建议安排技术负责人和业务负责人联合面试，重点验证知识库落地经验和协作方式。',
      dimScores: { project_experience: 92, skill_match: 96, education: 88, work_experience: 95, overall_quality: 90 },
    },
    {
      id: 2, name: 'Michael Chen', role: '高级前端工程师', stage: '初筛通过',
      aiScore: 91, match: 92, riskLabel: '到岗需确认', riskLevel: 'medium',
      recommendedAction: '补充到岗时间确认', location: '杭州', availableIn: '6 周到岗',
      reason: 'Vue、TypeScript 和复杂工作台项目经验突出，和前端岗位要求匹配。',
      skillMatch: 'Vue 3、组件抽象、数据可视化能力较强，企业 SaaS 经验充足。',
      experienceMatch: '5 年前端经验，最近项目和招聘工作台场景相近。',
      riskDetail: '离职交接周期较长，可能影响紧急岗位入职节奏。',
      interviewAdvice: '建议先安排远程技术面，验证复杂表格、权限 UI 和性能优化经验。',
      dimScores: { project_experience: 88, skill_match: 94, education: 82, work_experience: 85, overall_quality: 88 },
    },
    {
      id: 3, name: 'Sarah Jenkins', role: '产品经理', stage: '待复核',
      aiScore: 87, match: 86, riskLabel: '薪资偏高', riskLevel: 'medium',
      recommendedAction: '薪资范围预沟通', location: '北京', availableIn: '3 周到岗',
      reason: '招聘产品和数据分析经验较好，候选人对 HR 场景理解充分。',
      skillMatch: '需求分析、流程设计、指标拆解匹配，数据建模经验略弱。',
      experienceMatch: '有招聘管理平台经验，但权限审计类项目经历较少。',
      riskDetail: '期望薪资高于当前职级预算上沿，需要提前沟通。',
      interviewAdvice: '建议面试中加入业务流程建模题，观察其对多角色协作的拆解能力。',
      dimScores: { project_experience: 82, skill_match: 85, education: 90, work_experience: 80, overall_quality: 92 },
    },
    {
      id: 4, name: '刘伟', role: '后端工程师', stage: '简历筛选',
      aiScore: 82, match: 79, riskLabel: '技能缺口', riskLevel: 'high',
      recommendedAction: '补充项目材料', location: '广州', availableIn: '2 周到岗',
      reason: 'FastAPI 和数据库经验可用，但 Agent 工具链项目经验不足。',
      skillMatch: 'Python、SQLAlchemy、PostgreSQL 匹配，LangGraph 和 RAG 经验较弱。',
      experienceMatch: '后端服务经验稳定，缺少复杂 HR 权限链路项目经历。',
      riskDetail: '需要确认其对权限边界和审计日志的理解深度。',
      interviewAdvice: '建议增加系统设计题，重点询问模块化单体、权限校验和审计追踪。',
      dimScores: { project_experience: 68, skill_match: 78, education: 85, work_experience: 72, overall_quality: 75 },
    },
  ];
}

// ── 计算属性 ─────────────────────────────────
const summaryCards = computed(() => [
  { label: '候选人总数', value: String(candidates.value.length), icon: 'groups' },
  { label: '高匹配候选人', value: String(candidates.value.filter((c) => c.match >= 90).length), icon: 'verified' },
  { label: '需复核风险', value: String(candidates.value.filter((c) => c.riskLevel !== 'low').length), icon: 'warning' },
]);

const visibleCandidates = computed(() => {
  let list = highMatchOnly.value
    ? candidates.value.filter((c) => c.match >= 90)
    : [...candidates.value];

  if (filterMode.value === 'smart') {
    list.sort((a, b) => computedScore(b) - computedScore(a));
  } else if (filterMode.value === 'score') {
    list.sort((a, b) => computedScore(b) - computedScore(a));
  }

  return list;
});

const selectedCandidate = computed(() =>
  candidates.value.find((c) => c.id === selectedId.value) ?? candidates.value[0]
);

const filterHint = computed(() => {
  if (highMatchOnly.value) return '当前仅展示岗位匹配度 90% 及以上候选人。';
  if (filterMode.value === 'score') return '当前按加权评分从高到低排序。';
  if (filterMode.value === 'smart') return '当前综合评分、匹配度和风险标签进行优先级排序。';
  return '调整上方权重滑块后，评分和排序将实时更新。';
});

// ── 方法 ─────────────────────────────────────
/** 根据当前权重计算加权总分 */
function computedScore(candidate: Candidate): number {
  let total = 0;
  let totalWeight = 0;
  for (const dim of weightDimensions) {
    const w = weights[dim.key];
    const s = candidate.dimScores[dim.key] ?? 0;
    total += w * s;
    totalWeight += w;
  }
  if (totalWeight === 0) return 0;
  return Math.round(total / totalWeight);
}

function getDimensionScore(candidateId: number, dimKey: string): number {
  const c = candidates.value.find((c) => c.id === candidateId);
  return c?.dimScores[dimKey] ?? 0;
}

function updateWeight(key: string, value: number) {
  weights[key] = value;
  // 反馈给用户
  emit('show-toast', `${weightDimensions.find((d) => d.key === key)?.label} 权重已调整为 ${value}%。`);
}

function resetWeights() {
  Object.assign(weights, defaultWeights);
  emit('show-toast', '权重已恢复为默认值。');
}

function applySmartFilter() {
  filterMode.value = 'smart';
  highMatchOnly.value = true;
  selectedId.value = visibleCandidates.value[0]?.id ?? candidates.value[0]?.id;
  emit('show-toast', '已按岗位匹配度和风险标签完成智能筛选。');
}

function sortByScore() {
  filterMode.value = 'score';
  selectedId.value = visibleCandidates.value[0]?.id ?? candidates.value[0]?.id;
  emit('show-toast', '候选人已按加权评分降序排列。');
}

function toggleHighMatch() {
  highMatchOnly.value = !highMatchOnly.value;
  selectedId.value = visibleCandidates.value[0]?.id ?? candidates.value[0]?.id;
  emit('show-toast', highMatchOnly.value ? '已切换为只看高匹配候选人。' : '已恢复查看全部候选人。');
}

function selectCandidate(candidate: Candidate) {
  selectedId.value = candidate.id;
  emit('show-toast', `已打开 ${candidate.name} 的综合评估。`);
}

function scheduleInterview(candidate: Candidate) {
  emit('show-toast', `正在为 ${candidate.name} 准备面试排期建议。`);
  setTimeout(() => emit('navigate', 'interviews'), 500);
}

function stageClass(stage: string) {
  return {
    'tag tag--blue': stage.includes('约面') || stage.includes('初筛'),
    'tag tag--amber': stage.includes('复核') || stage.includes('筛选'),
  };
}

function riskClass(level: Candidate['riskLevel']) {
  return {
    'tag tag--green': level === 'low',
    'tag tag--amber': level === 'medium',
    'tag tag--red': level === 'high',
  };
}

function retry() {
  loading.value = false;
  error.value = null;
  initData();
}

// ── 初始化 ───────────────────────────────────
initData();
// 模拟加载完成
setTimeout(() => {
  loading.value = false;
  selectedId.value = candidates.value[0]?.id ?? 0;
}, 400);
</script>

<style scoped>
/* ═══ 权重沙盘 ═══ */
.weight-sandbox {
  max-width: 1440px;
  margin: 0 auto 22px;
  padding: 20px 24px;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, rgba(36,85,245,0.03), rgba(36,85,245,0.01));
  box-shadow: 0 2px 12px rgba(36,85,245,0.06);
}

/* 嵌入 content grid 左列时取消外部约束 */
.weight-sandbox--inline {
  max-width: none;
  margin: 0;
}

.weight-sandbox__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.weight-sandbox__header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: var(--color-primary);
}

.weight-sandbox__reset {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.15s;
}

.weight-sandbox__reset:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.weight-sandbox__sliders {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 18px;
}

.weight-slider__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.weight-slider__header label {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-muted);
}

.weight-slider__value {
  font-size: 14px;
  font-weight: 900;
  color: var(--color-primary);
  font-variant-numeric: tabular-nums;
}

.weight-slider__input {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  border-radius: 3px;
  background: var(--color-line);
  outline: none;
  cursor: pointer;
}

.weight-slider__input::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-primary);
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 2px 6px rgba(36,85,245,0.25);
  cursor: pointer;
}

.weight-sandbox__hint {
  margin: 14px 0 0;
  font-size: 12px;
  color: var(--color-subtle);
  line-height: 1.5;
}

/* ═══ 评分分解 ═══ */
.score-breakdown {
  padding: 12px;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  background: var(--color-surface-soft);
}

.score-breakdown h4 {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 800;
  color: var(--color-muted);
}

.score-breakdown__row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 5px;
}

.score-breakdown__row:last-child {
  margin-bottom: 0;
}

.score-breakdown__label {
  font-size: 12px;
  color: var(--color-muted);
  white-space: nowrap;
  width: 56px;
  font-weight: 600;
}

.score-breakdown__bar-bg {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--color-line);
  overflow: hidden;
}

.score-breakdown__bar {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #7dd3fc, #38bdf8);
  transition: width 0.3s ease;
}

.score-breakdown__val {
  font-size: 13px;
  font-weight: 800;
  color: var(--color-primary);
  min-width: 28px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

/* ═══ 原有样式（保持兼容） ═══ */
.candidate-pool {
  display: grid;
  gap: 22px;
}

.candidate-pool__hero,
.candidate-pool__summary,
.candidate-pool__content {
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
}

.candidate-pool__hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
}

.candidate-pool__eyebrow {
  margin: 0 0 8px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 800;
}

.candidate-pool__hero h2 {
  margin: 0;
  color: var(--color-text);
  font-size: 30px;
  line-height: 1.15;
}

.candidate-pool__hero p {
  margin: 8px 0 0;
  color: var(--color-muted);
}

.candidate-pool__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 40px;
  padding: 0 14px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-text);
  font-weight: 800;
  cursor: pointer;
  transition: 0.2s ease;
}

.btn:hover,
.btn--active {
  border-color: rgba(36,85,245,0.35);
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.btn--primary {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: #fff;
}

.btn--primary:hover {
  background: #173fd1;
  color: #fff;
}

.candidate-pool__summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.metric-card > span {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 12px;
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.metric-card strong,
.metric-card small {
  display: block;
}

.metric-card strong {
  color: var(--color-text);
  font-size: 26px;
}

.metric-card small {
  color: var(--color-muted);
  font-weight: 700;
}

.candidate-pool__content {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(360px, 0.9fr);
  gap: 18px;
  align-items: start;
}

.candidate-table-card,
.candidate-detail-card {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.candidate-table-card {
  overflow: hidden;
}

.candidate-table-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-bottom: 1px solid var(--color-line);
}

.candidate-table-card__header h3,
.candidate-detail-card__header h3 {
  margin: 0;
  color: var(--color-text);
}

.candidate-table-card__header p,
.candidate-detail-card__header p,
.candidate-detail-card__header small {
  margin: 4px 0 0;
  color: var(--color-muted);
}

.candidate-table-card__header > span {
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--color-surface-soft);
  color: var(--color-muted);
  font-weight: 800;
}

.candidate-table {
  display: grid;
}

.candidate-row {
  display: grid;
  grid-template-columns: minmax(160px,1.3fr) minmax(130px,1fr) 92px 78px minmax(120px,0.9fr) 112px minmax(150px,1fr);
  gap: 12px;
  align-items: center;
  width: 100%;
  padding: 16px 20px;
  border: 0;
  border-bottom: 1px solid var(--color-line);
  background: transparent;
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
  transition: 0.18s ease;
}

.candidate-row:hover,
.candidate-row--selected {
  background: #f7f9ff;
}

.candidate-row:last-child {
  border-bottom: 0;
}

.candidate-row__name strong,
.candidate-row__name small,
.candidate-row__action strong {
  display: block;
}

.candidate-row__name small {
  margin-top: 4px;
  color: var(--color-muted);
  font-size: 12px;
}

.candidate-row .score {
  color: var(--color-primary);
  font-size: 22px;
  font-weight: 900;
}

.candidate-row__action strong {
  margin-bottom: 5px;
  font-size: 13px;
}

.link-button {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.match-bar {
  display: block;
  height: 8px;
  margin-bottom: 5px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--color-surface-soft);
}

.match-bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #2455f5, #16a34a);
}

.tag {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 8px;
  border-radius: 999px;
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.tag--blue {
  background: #eaf0ff;
  color: #2455f5;
}

.tag--green {
  background: #dcfce7;
  color: #15803d;
}

.tag--amber {
  background: #fff7ed;
  color: #c2410c;
}

.tag--red {
  background: #fee2e2;
  color: #b91c1c;
}

.candidate-detail-card {
  grid-column: 2;
  grid-row: 1;
  position: sticky;
  top: 92px;
  display: grid;
  gap: 14px;
  padding: 16px;
}

.candidate-detail-card__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-line);
}

.candidate-detail-card__score {
  display: grid;
  min-width: 92px;
  place-items: center;
  padding: 12px;
  border-radius: 16px;
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.candidate-detail-card__score strong {
  font-size: 32px;
  line-height: 1;
}

.candidate-detail-card__score span {
  margin-top: 5px;
  font-size: 12px;
  font-weight: 800;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.detail-grid article,
.interview-advice {
  padding: 14px;
  border: 1px solid var(--color-line);
  border-radius: 14px;
  background: var(--color-surface-soft);
}

.detail-grid article span,
.interview-advice span {
  color: var(--color-primary);
}

.detail-grid article strong,
.interview-advice strong {
  display: block;
  margin-top: 6px;
  color: var(--color-text);
}

.detail-grid article p,
.interview-advice p {
  margin: 7px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.55;
}

.interview-advice > div {
  display: flex;
  align-items: center;
  gap: 8px;
}

.interview-advice strong {
  margin-top: 0;
}

.candidate-detail-card__footer {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

@media (max-width: 1180px) {
  .weight-sandbox__sliders {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .candidate-pool__content {
    grid-template-columns: 1fr;
  }

  .candidate-detail-card {
    position: static;
  }
}

@media (max-width: 860px) {
  .candidate-pool__hero {
    align-items: stretch;
    flex-direction: column;
  }

  .candidate-pool__actions {
    justify-content: flex-start;
  }

  .candidate-pool__summary,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .candidate-row {
    grid-template-columns: 1fr;
  }
}
</style>
