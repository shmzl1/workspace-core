<template>
  <div class="h-full flex flex-col bg-background">
    <LoadingState v-if="loading" message="正在获取面试日程..." detail="正在读取面试安排与资源可用时间" />

    <PermissionDenied
      v-else-if="permissionDenied"
      description="你当前的角色无权访问面试日历，如需协助请联系 HR 管理员。"
    />

    <template v-else>
      <div class="max-w-container-max mx-auto space-y-gutter">
        <div class="flex items-end justify-between gap-4">
          <div>
            <p class="font-label-md text-label-md text-primary uppercase tracking-wider mb-1">招聘流程</p>
            <h2 class="font-headline-lg text-headline-lg-mobile text-on-surface tracking-tight">面试日历</h2>
            <p class="font-body-md text-body-md text-on-surface-variant mt-1">统一管理候选人、面试官、会议室和时间槽。</p>
          </div>
          <button
            class="flex items-center gap-2 px-5 py-3 bg-primary text-on-primary rounded-xl font-label-md font-semibold shadow-md hover:shadow-lg hover:bg-primary-fixed-dim hover:text-on-primary-fixed transition-all disabled:opacity-50 disabled:cursor-wait"
            :disabled="generating || applications.length === 0"
            @click="generateSchedule"
          >
            <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
            {{ generating ? '排期中...' : '智能排期' }}
          </button>
        </div>

        <div v-if="serviceError" class="flex items-center justify-between gap-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          <div>
            <strong class="block">服务暂不可用，请确认后端已启动。</strong>
            <span>{{ serviceError }}</span>
          </div>
          <button class="rounded-lg bg-primary px-4 py-2 font-semibold text-white" @click="loadInterviewData">
            重新加载
          </button>
        </div>

        <p v-else-if="scheduleNotice" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-semibold text-amber-800">
          {{ scheduleNotice }}
        </p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-gutter">
          <div class="glass-card rounded-xl p-6 relative overflow-hidden">
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">今日面试总数</p>
                <h2 class="font-display text-display text-on-surface mt-1">{{ scheduleItems.length }}</h2>
              </div>
              <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined">event</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="font-body-md text-body-md text-secondary flex items-center gap-1">
                <span class="material-symbols-outlined text-[16px]">database</span> 数据库
              </span>
              <span class="font-label-md text-label-md text-on-surface-variant">今日实时日程</span>
            </div>
          </div>

          <div class="glass-card rounded-xl p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">待评价面试</p>
                <h2 class="font-display text-display text-on-surface mt-1">{{ pendingEvaluationCount }}</h2>
              </div>
              <div class="w-10 h-10 rounded-lg bg-[#FFF7ED] flex items-center justify-center text-[#EA580C]">
                <span class="material-symbols-outlined">rate_review</span>
              </div>
            </div>
            <div class="w-full bg-surface-container h-2 rounded-full mt-4 overflow-hidden">
              <div class="bg-[#EA580C] h-full rounded-full" :style="{ width: `${pendingEvaluationRate}%` }"></div>
            </div>
          </div>

          <div class="glass-card rounded-xl p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">平均面试时长</p>
                <h2 class="font-display text-display text-on-surface mt-1">{{ averageDuration }}<span class="font-headline-md text-headline-md ml-1 text-on-surface-variant">min</span></h2>
              </div>
              <div class="w-10 h-10 rounded-lg bg-tertiary/10 flex items-center justify-center text-tertiary">
                <span class="material-symbols-outlined">timer</span>
              </div>
            </div>
            <div class="flex items-center gap-2 mt-4">
              <span class="material-symbols-outlined text-secondary text-[16px]">check_circle</span>
              <span class="font-label-md text-label-md text-on-surface-variant">符合标准预期时长</span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-gutter min-h-[520px]">
          <div class="lg:col-span-4 glass-card rounded-xl p-6 flex flex-col h-full">
            <div class="flex justify-between items-center mb-6">
              <h3 class="font-title-lg text-title-lg text-on-surface">2026 年 7 月</h3>
              <div class="flex bg-surface-container-low rounded-lg p-1">
                <button
                  class="px-3 py-1 rounded font-label-md text-label-md transition-colors"
                  :class="calendarView === 'month' ? 'bg-white shadow-sm text-on-surface' : 'text-on-surface-variant hover:text-on-surface'"
                  @click="calendarView = 'month'"
                >月视图</button>
                <button
                  class="px-3 py-1 rounded font-label-md text-label-md transition-colors"
                  :class="calendarView === 'week' ? 'bg-white shadow-sm text-on-surface' : 'text-on-surface-variant hover:text-on-surface'"
                  @click="calendarView = 'week'"
                >周视图</button>
              </div>
            </div>

            <div class="grid grid-cols-7 gap-2 mb-2">
              <div v-for="day in weekdays" :key="day" class="text-center font-label-md text-label-md text-on-surface-variant py-2">{{ day }}</div>
            </div>

            <div class="flex-1 grid grid-cols-7 gap-2 auto-rows-min content-start">
              <button
                v-for="day in calendarDays"
                :key="day.date"
                class="text-center py-2 rounded-lg font-label-md text-label-md transition-colors relative"
                :class="{
                  'text-outline': day.muted,
                  'text-on-surface': !day.muted,
                  'bg-primary text-on-primary rounded-full font-bold shadow-md shadow-primary/30': day.today && !scheduleGenerated,
                  'bg-emerald-500 text-white rounded-full font-bold shadow-md': scheduleGenerated && day.recommended && !day.conflict,
                  'bg-red-500 text-white rounded-full font-bold shadow-md': scheduleGenerated && day.conflict,
                  'hover:bg-surface-container-low': !day.today,
                }"
              >
                {{ day.date }}
                <span v-if="!day.muted && day.events > 0 && !day.today" class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full"></span>
              </button>
            </div>

            <div class="mt-4 pt-4 border-t border-outline-variant">
              <h4 class="font-label-md text-label-md text-on-surface-variant mb-2">排期建议</h4>
              <div class="bg-surface-bright border border-primary/20 rounded-lg p-3 flex gap-3 items-start">
                <span class="material-symbols-outlined text-primary text-[20px]">event_available</span>
                <div class="space-y-1">
                  <p class="font-body-md text-body-md text-on-surface text-sm">{{ currentSuggestion.reason }}</p>
                  <p class="text-xs text-on-surface-variant">推荐时间：{{ currentSuggestion.time }}</p>
                  <button class="text-primary font-label-md text-label-md mt-1 hover:underline" @click="generateSchedule">刷新建议</button>
                </div>
              </div>
            </div>
          </div>

          <div class="lg:col-span-8 glass-card rounded-xl p-0 flex flex-col h-full overflow-hidden">
            <div class="p-6 border-b border-outline-variant flex justify-between items-center bg-surface/50">
              <h3 class="font-title-lg text-title-lg text-on-surface">今日面试日程</h3>
              <span
                class="px-3 py-1 rounded-lg font-label-md text-label-md"
                :class="scheduleGenerated ? 'bg-emerald-50 text-emerald-700' : 'bg-surface-container text-on-surface-variant'"
              >{{ scheduleGenerated ? '已生成排期建议' : '共 ' + scheduleItems.length + ' 场' }}</span>
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-0 flex-1 overflow-hidden">
              <div class="overflow-y-auto p-6 space-y-4">
                <EmptyState
                  v-if="scheduleItems.length === 0"
                  title="暂无今日日程"
                  description="今天没有安排面试，可以点击上方智能排期按钮生成推荐日程。"
                />

                <div
                  v-for="item in scheduleItems"
                  :key="item.time + item.candidate"
                  class="border rounded-xl p-4 flex items-center gap-6 relative shadow-sm transition-colors"
                  :class="{
                    'border-primary/20 bg-primary/5': scheduleGenerated && item.recommended && !item.hasConflict,
                    'border-[#EA580C]/20 bg-[#FFF7ED]': item.hasConflict,
                    'border-outline-variant bg-white hover:border-primary/50': !scheduleGenerated || (!item.recommended && !item.hasConflict),
                  }"
                >
                  <div v-if="scheduleGenerated && item.recommended && !item.hasConflict" class="absolute left-0 top-0 bottom-0 w-1.5 bg-emerald-500 rounded-l-lg"></div>
                  <div v-if="item.hasConflict" class="absolute left-0 top-0 bottom-0 w-1.5 bg-[#EA580C] rounded-l-lg"></div>

                  <div class="flex flex-col items-center justify-center min-w-[80px]">
                    <span class="font-headline-md text-headline-md font-bold" :class="scheduleGenerated && item.recommended && !item.hasConflict ? 'text-emerald-600' : 'text-primary'">{{ item.time }}</span>
                    <span class="font-label-md text-label-md text-on-surface-variant">{{ item.duration }}</span>
                    <span
                      v-if="scheduleGenerated"
                      class="mt-1 px-2 py-0.5 font-label-md text-[10px] rounded"
                      :class="{
                        'bg-emerald-100 text-emerald-700': item.recommended && !item.hasConflict,
                        'bg-[#FFEDD5] text-[#EA580C]': item.hasConflict,
                      }"
                    >{{ item.status }}</span>
                  </div>

                  <div class="w-12 h-12 rounded-full bg-surface-container-high flex items-center justify-center shrink-0 text-on-surface-variant font-bold text-lg">
                    {{ item.candidate.charAt(0) }}
                  </div>

                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <h4 class="font-title-lg text-title-lg text-on-surface">{{ item.candidate }}</h4>
                      <span class="px-2 py-0.5 bg-surface-container text-on-surface-variant rounded text-xs font-label-md">{{ item.role }}</span>
                    </div>
                    <div class="flex flex-wrap items-center gap-4 font-body-md text-body-md text-on-surface-variant text-sm">
                      <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">person</span> 面试官 {{ item.interviewer }}</span>
                      <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">{{ item.room.includes('线上') ? 'videocam' : 'location_on' }}</span> {{ item.room }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <aside class="border-l border-outline-variant bg-surface/40 p-6 space-y-4 overflow-y-auto">
                <div>
                  <p class="font-label-md text-label-md text-primary uppercase tracking-wider">智能排期</p>
                  <h3 class="font-title-lg text-title-lg text-on-surface mt-1">排期建议</h3>
                </div>

                <!-- Candidate Selection Dropdown -->
                <div v-if="applications.length > 0" class="space-y-1">
                  <label for="candidate-select" class="text-xs font-semibold text-on-surface-variant block">选择排期候选人：</label>
                  <select id="candidate-select" v-model="selectedApplicationId" class="w-full bg-white border border-outline-variant rounded-lg p-2.5 text-sm outline-none focus:border-primary cursor-pointer font-semibold">
                    <option v-for="app in applications" :key="app.id" :value="app.id">
                      {{ applicationLabel(app) }}
                    </option>
                  </select>
                </div>
                <p v-else class="rounded-lg bg-surface-container-low p-3 text-sm text-on-surface-variant">
                  暂无可排期候选人，请先在候选人池创建申请记录。
                </p>

                <div class="rounded-xl border border-outline-variant bg-white p-4 space-y-3">
                  <div>
                    <span class="text-xs text-on-surface-variant">推荐时间段</span>
                    <p class="font-semibold text-on-surface">{{ currentSuggestion.time }}</p>
                  </div>
                  <div>
                    <span class="text-xs text-on-surface-variant">面试官可用时间</span>
                    <p class="font-body-md text-body-md text-on-surface">{{ currentSuggestion.interviewerAvailability }}</p>
                  </div>
                  <div>
                    <span class="text-xs text-on-surface-variant">候选人可用时间</span>
                    <p class="font-body-md text-body-md text-on-surface">{{ currentSuggestion.candidateAvailability }}</p>
                  </div>
                  <div>
                    <span class="text-xs text-on-surface-variant">冲突检测</span>
                    <p class="font-body-md text-body-md text-on-surface">{{ currentSuggestion.conflict }}</p>
                  </div>
                  <div>
                    <span class="text-xs text-on-surface-variant">推荐理由</span>
                    <p class="font-body-md text-body-md text-on-surface">{{ currentSuggestion.reason }}</p>
                  </div>
                  <div>
                    <span class="text-xs text-on-surface-variant">推荐评分</span>
                    <p class="font-semibold text-primary">{{ currentSuggestion.score }}</p>
                  </div>
                  <button
                    v-if="scheduleGenerated && selectedPreview"
                    class="w-full rounded-lg bg-primary px-4 py-2.5 font-semibold text-white transition-colors hover:bg-primary-fixed-dim disabled:cursor-wait disabled:opacity-50"
                    :disabled="confirming || currentSuggestion.hasConflict"
                    @click="confirmSchedule"
                  >
                    {{ confirming ? '保存中...' : '确认面试安排' }}
                  </button>
                </div>
              </aside>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import EmptyState from '../shared/components/feedback/EmptyState.vue';
import PermissionDenied from '../shared/components/feedback/PermissionDenied.vue';
import {
  fetchInterviews,
  fetchInterviewers,
  fetchMeetingRooms,
  confirmInterviewSchedule,
  generateInterviewSchedule,
  type InterviewerResource,
  type MeetingRoomResource,
} from '../shared/api/modules/interview';
import { fetchApplications, fetchCandidates, fetchJobs } from '../shared/api/modules/recruitment';
import type { CandidateApplicationListItem } from '../shared/api/modules/recruitment';
import type {
  Candidate as ApiCandidate,
  Job as ApiJob,
  SchedulePreviewRequest,
  SchedulePreviewResponse,
} from '../shared/api/types';
import { checkBackendHealth } from '../shared/api/modules/health';
import { ApiClientError } from '../shared/api/apiClient';

const route = useRoute();
const applications = ref<CandidateApplicationListItem[]>([]);
const selectedApplicationId = ref<number | null>(null);
const candidates = ref<ApiCandidate[]>([]);
const jobs = ref<ApiJob[]>([]);
const interviewerResources = ref<InterviewerResource[]>([]);
const roomResources = ref<MeetingRoomResource[]>([]);

type ScheduleItem = {
  time: string;
  duration: string;
  candidate: string;
  role: string;
  interviewer: string;
  room: string;
  status: string;
  recommended: boolean;
  hasConflict: boolean;
};

type Suggestion = {
  time: string;
  interviewerAvailability: string;
  candidateAvailability: string;
  conflict: string;
  reason: string;
  score: number | string;
  hasConflict: boolean;
};

const emit = defineEmits<{
  'show-toast': [message: string];
}>();

const loading = ref(true);
const permissionDenied = ref(false);
const scheduleGenerated = ref(false);
const generating = ref(false);
const confirming = ref(false);
const calendarView = ref<'month' | 'week'>('month');
const apiSuggestion = ref<Suggestion | null>(null);
const selectedPreview = ref<SchedulePreviewResponse | null>(null);
const scheduleNotice = ref('');
const serviceError = ref('');

const weekdays = ['一', '二', '三', '四', '五', '六', '日'];

const scheduleItems = ref<ScheduleItem[]>([]);

const currentSuggestion = computed<Suggestion>(() => apiSuggestion.value ?? {
  time: '等待生成',
  interviewerAvailability: '请选择候选人后生成排期建议。',
  candidateAvailability: '等待读取候选人可用时间。',
  conflict: '尚未检测',
  reason: '排期结果将基于数据库中的申请、面试官、会议室和已有日程生成。',
  score: '--',
  hasConflict: false,
});
const pendingEvaluationCount = computed(() => scheduleItems.value.filter((item) => item.status === '待评价').length);
const pendingEvaluationRate = computed(() => (
  scheduleItems.value.length ? Math.round(pendingEvaluationCount.value / scheduleItems.value.length * 100) : 0
));
const averageDuration = computed(() => {
  if (!scheduleItems.value.length) return 0;
  const total = scheduleItems.value.reduce((sum, item) => sum + (Number.parseInt(item.duration) || 0), 0);
  return Math.round(total / scheduleItems.value.length);
});

const calendarDays = ref<Array<{ date: number; muted: boolean; today: boolean; events: number; recommended: boolean; conflict: boolean }>>([]);

onMounted(loadInterviewData);

async function loadInterviewData() {
  loading.value = true;
  serviceError.value = '';
  scheduleNotice.value = '';
  permissionDenied.value = false;
  try {
    await checkBackendHealth();
    const [appRows, candidateRows, jobRows, interviewerRows, roomRows, interviewRows] = await Promise.all([
      fetchApplications(),
      fetchCandidates(),
      fetchJobs(),
      fetchInterviewers(),
      fetchMeetingRooms(),
      fetchInterviews(),
    ]);
    applications.value = appRows;
    candidates.value = candidateRows;
    jobs.value = jobRows;
    interviewerResources.value = interviewerRows;
    roomResources.value = roomRows;
    calendarDays.value = buildCalendarDays(interviewRows);
    const today = new Date().toDateString();
    scheduleItems.value = interviewRows
      .filter((interview) => new Date(interview.start_at).toDateString() === today)
      .map((interview) => {
        const application = appRows.find((item) => item.id === interview.application_id);
        return {
          time: formatClock(new Date(interview.start_at)),
          duration: `${Math.round((new Date(interview.end_at).getTime() - new Date(interview.start_at).getTime()) / 60000)} 分钟`,
          candidate: candidateName(application),
          role: jobName(application),
          interviewer: interviewerName(interview.interviewer_id),
          room: roomName(interview.meeting_room_id),
          status: interview.status === 'COMPLETED' ? '待评价' : interview.status === 'SCHEDULED' ? '已安排' : interview.status,
          recommended: false,
          hasConflict: false,
        };
      });
    
    // Parse query parameter applicationId
    const queryAppId = Number(route.query.applicationId);
    if (queryAppId && appRows.some(a => a.id === queryAppId)) {
      selectedApplicationId.value = queryAppId;
    } else if (appRows.length > 0) {
      selectedApplicationId.value = appRows[0].id;
    }
  } catch (err: any) {
    applications.value = [];
    candidates.value = [];
    jobs.value = [];
    interviewerResources.value = [];
    roomResources.value = [];
    scheduleItems.value = [];
    if (err instanceof ApiClientError && err.status === 403) {
      permissionDenied.value = true;
    } else {
      serviceError.value = err.message || '网络连接失败，服务端未响应。';
    }
  } finally {
    loading.value = false;
  }
}

async function generateSchedule() {
  if (generating.value) return;
  if (!selectedApplicationId.value) {
    scheduleNotice.value = '暂无可排期候选人，请先在候选人池创建申请记录。';
    return;
  }
  if (!interviewerResources.value.length || !roomResources.value.length) {
    scheduleNotice.value = '缺少面试官或会议室数据，当前无法生成排期建议。';
    return;
  }
  generating.value = true;
  try {
    const result = await generateInterviewSchedule(buildSchedulePayload());
    if (result.status === 'algorithm_not_ready' || !result.recommended_time) {
      throw new Error(result.message || '暂时没有可用排期建议。');
    }
    applyScheduleResult(result);
    selectedPreview.value = result;
    scheduleNotice.value = '';
    emit('show-toast', '已生成智能排期建议。');
  } catch (error: any) {
    scheduleGenerated.value = false;
    scheduleNotice.value = error.message || '智能排期暂时无法获取，请稍后重试。';
    emit('show-toast', scheduleNotice.value);
  } finally {
    generating.value = false;
  }
}

function buildSchedulePayload(): SchedulePreviewRequest {
  const currentAppId = selectedApplicationId.value;
  const currentApp = applications.value.find(a => a.id === currentAppId);
  if (!currentApp) throw new Error('选中的候选人申请不存在，请刷新页面后重试。');
  return {
    application_id: currentApp.id,
    duration_minutes: 60,
  };
}

function applicationLabel(application: CandidateApplicationListItem): string {
  return `${candidateName(application)} - ${jobName(application)}`;
}

function candidateName(application?: CandidateApplicationListItem): string {
  const joinedName = String(application?.candidate_name || '').trim();
  if (joinedName) return joinedName;
  const candidate = candidates.value.find((item) => item.id === application?.candidate_id);
  return String(candidate?.full_name || '').trim() || '未命名候选人';
}

function jobName(application?: CandidateApplicationListItem): string {
  const joinedTitle = String(application?.job_title || '').trim();
  if (joinedTitle) return joinedTitle;
  const job = jobs.value.find((item) => item.id === application?.job_id);
  return String(job?.title || '').trim() || '待匹配岗位';
}

function interviewerName(interviewerId?: number | null): string {
  const interviewer = interviewerResources.value.find((item) => item.id === Number(interviewerId));
  return String(interviewer?.employee_name || '').trim()
    || (interviewer ? `员工 #${interviewer.employee_id}` : '待分配面试官');
}

function roomName(roomId?: number | null): string {
  const room = roomResources.value.find((item) => item.id === Number(roomId));
  return String(room?.name || '').trim() || (room ? `会议室 #${room.id}` : '待分配会议室');
}

function applyScheduleResult(result: SchedulePreviewResponse) {
  const start = String(result.recommended_time?.start || '');
  const end = String(result.recommended_time?.end || '');
  if (!start || !end) throw new Error('排期建议缺少完整的开始或结束时间。');
  const startDate = new Date(start);
  const endDate = new Date(end);
  const timeLabel = `${formatClock(startDate)} - ${formatClock(endDate)}`;
  const score = Number(result.conflict_explanation?.priority_score ?? 90);

  const currentAppId = selectedApplicationId.value;
  const currentApp = applications.value.find(a => a.id === currentAppId);
  const selectedCandidateName = candidateName(currentApp);
  const roleName = jobName(currentApp);

  apiSuggestion.value = {
    time: `7 月 ${startDate.getDate()} 日 ${timeLabel}`,
    interviewerAvailability: result.interviewer_availability || '面试官在该时间段可用。',
    candidateAvailability: result.candidate_availability || '候选人在该时间段可用。',
    conflict: result.conflict_detection || '未发现冲突。',
    reason: result.recommendation_reason || '该时间段满足候选人、面试官和会议室可用条件。',
    score,
    hasConflict: Boolean(result.conflict_explanation?.conflicts && Array.isArray(result.conflict_explanation.conflicts) && result.conflict_explanation.conflicts.length),
  };

  scheduleGenerated.value = true;
  markCalendarDay(startDate.getDate(), apiSuggestion.value.hasConflict);
  scheduleItems.value = [
    {
      time: formatClock(startDate),
      duration: `${Math.max(30, Math.round((endDate.getTime() - startDate.getTime()) / 60000))} 分钟`,
      candidate: selectedCandidateName,
      role: roleName,
      interviewer: interviewerName(result.recommended_interviewer_id),
      room: roomName(result.recommended_room_id),
      status: '推荐时段',
      recommended: true,
      hasConflict: apiSuggestion.value.hasConflict,
    },
    ...scheduleItems.value.filter((item) => !item.recommended).slice(0, 2),
  ];
}

async function confirmSchedule() {
  const preview = selectedPreview.value;
  if (!preview?.recommended_time || confirming.value) return;
  const applicationId = selectedApplicationId.value;
  const interviewerId = preview.recommended_interviewer_id;
  const roomId = preview.recommended_room_id;
  const startAt = String(preview.recommended_time.start || '');
  const endAt = String(preview.recommended_time.end || '');
  if (!applicationId || !interviewerId || !roomId || !startAt || !endAt) {
    scheduleNotice.value = '排期建议信息不完整，请重新生成。';
    return;
  }
  confirming.value = true;
  try {
    await confirmInterviewSchedule({
      application_id: applicationId,
      interviewer_id: interviewerId,
      meeting_room_id: roomId,
      start_at: startAt,
      end_at: endAt,
      conflict_explanation: preview.conflict_explanation || {},
    });
    selectedPreview.value = null;
    apiSuggestion.value = null;
    scheduleGenerated.value = false;
    await loadInterviewData();
    emit('show-toast', '面试安排已保存，日历已刷新。');
  } catch (error) {
    const message = error instanceof Error ? error.message : '面试安排保存失败。';
    scheduleNotice.value = message;
    emit('show-toast', message);
  } finally {
    confirming.value = false;
  }
}

function markCalendarDay(date: number, hasConflict: boolean) {
  calendarDays.value = calendarDays.value.map((day) => ({
    ...day,
    recommended: day.date === date ? true : day.recommended,
    conflict: day.date === date ? hasConflict : day.conflict,
  }));
}

function buildCalendarDays(interviews: Array<{ start_at: string }>) {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const first = new Date(year, month, 1);
  const startOffset = (first.getDay() + 6) % 7;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const previousMonthDays = new Date(year, month, 0).getDate();
  const counts = new Map<number, number>();
  for (const interview of interviews) {
    const value = new Date(interview.start_at);
    if (value.getFullYear() === year && value.getMonth() === month) {
      counts.set(value.getDate(), (counts.get(value.getDate()) || 0) + 1);
    }
  }
  return Array.from({ length: 35 }, (_, index) => {
    const offsetDay = index - startOffset + 1;
    const muted = offsetDay < 1 || offsetDay > daysInMonth;
    const date = offsetDay < 1 ? previousMonthDays + offsetDay : offsetDay > daysInMonth ? offsetDay - daysInMonth : offsetDay;
    return {
      date,
      muted,
      today: !muted && date === now.getDate(),
      events: muted ? 0 : counts.get(date) || 0,
      recommended: false,
      conflict: false,
    };
  });
}

function formatClock(value: Date) {
  return value.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });
}
</script>
