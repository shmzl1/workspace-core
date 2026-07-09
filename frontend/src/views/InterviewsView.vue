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
            <h2 class="font-headline-lg md:font-display text-headline-lg-mobile md:text-display text-on-surface tracking-tight">面试日历</h2>
            <p class="font-body-md text-body-md text-on-surface-variant mt-1">统一管理候选人、面试官、会议室和时间槽。</p>
          </div>
          <button
            class="flex items-center gap-2 px-5 py-3 bg-primary text-on-primary rounded-xl font-label-md font-semibold shadow-md hover:shadow-lg hover:bg-primary-fixed-dim hover:text-on-primary-fixed transition-all disabled:opacity-50 disabled:cursor-wait"
            :disabled="generating"
            @click="generateSchedule"
          >
            <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
            {{ generating ? '排期中...' : '智能排期' }}
          </button>
        </div>

        <p v-if="scheduleNotice" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-semibold text-amber-800">
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
                <span class="material-symbols-outlined text-[16px]">trending_up</span> 20%
              </span>
              <span class="font-label-md text-label-md text-on-surface-variant">较昨日</span>
            </div>
          </div>

          <div class="glass-card rounded-xl p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">待评价面试</p>
                <h2 class="font-display text-display text-on-surface mt-1">4</h2>
              </div>
              <div class="w-10 h-10 rounded-lg bg-[#FFF7ED] flex items-center justify-center text-[#EA580C]">
                <span class="material-symbols-outlined">rate_review</span>
              </div>
            </div>
            <div class="w-full bg-surface-container h-2 rounded-full mt-4 overflow-hidden">
              <div class="bg-[#EA580C] h-full rounded-full" :style="{ width: '33%' }"></div>
            </div>
          </div>

          <div class="glass-card rounded-xl p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">平均面试时长</p>
                <h2 class="font-display text-display text-on-surface mt-1">45<span class="font-headline-md text-headline-md ml-1 text-on-surface-variant">min</span></h2>
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

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-gutter min-h-[600px]">
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
                      {{ app.candidate_name }} ({{ app.job_title }})
                    </option>
                  </select>
                </div>

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
import { generateInterviewSchedule } from '../shared/api/modules/interview';
import { fetchApplications } from '../shared/api/modules/recruitment';
import type { CandidateApplicationListItem } from '../shared/api/modules/recruitment';
import type { SchedulePreviewRequest, SchedulePreviewResponse } from '../shared/api/types';

const route = useRoute();
const applications = ref<CandidateApplicationListItem[]>([]);
const selectedApplicationId = ref<number | null>(null);

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
const calendarView = ref<'month' | 'week'>('month');
const activeSuggestionIndex = ref(0);
const apiSuggestion = ref<Suggestion | null>(null);
const scheduleNotice = ref('');

const weekdays = ['一', '二', '三', '四', '五', '六', '日'];

const scheduleItems = ref<ScheduleItem[]>([
  {
    time: '10:00',
    duration: '60 分钟',
    candidate: 'Eleanor Vance',
    role: '首席数据科学家',
    interviewer: '王刚',
    room: '线上会议室 A',
    status: '已确认',
    recommended: false,
    hasConflict: false,
  },
  {
    time: '14:00',
    duration: '45 分钟',
    candidate: 'Michael Chen',
    role: '高级前端工程师',
    interviewer: '林雨晴',
    room: '会议室 B-201',
    status: '待确认',
    recommended: false,
    hasConflict: false,
  },
]);

const suggestions = ref<Suggestion[]>([
  {
    time: '7 月 10 日 10:00 - 11:00',
    interviewerAvailability: '王刚 09:30 - 11:30 可用',
    candidateAvailability: '候选人确认上午时段可参加',
    conflict: '未发现冲突',
    reason: '候选人匹配度较高，且面试官与会议室在同一时间段均可用，建议优先安排。',
    score: 92,
    hasConflict: false,
  },
  {
    time: '7 月 16 日 15:00 - 15:45',
    interviewerAvailability: '林雨晴 14:30 - 16:00 可用',
    candidateAvailability: '候选人下午时段可用',
    conflict: '原 14:00 时段与会议室占用冲突',
    reason: '顺延后无需更换面试官，并能保留同一面试记录模板。',
    score: 81,
    hasConflict: true,
  },
]);

const currentSuggestion = computed(() => apiSuggestion.value ?? suggestions.value[activeSuggestionIndex.value]);

const calendarDays = ref([
  { date: 29, muted: true, today: false, events: 0, recommended: false, conflict: false },
  { date: 30, muted: true, today: false, events: 0, recommended: false, conflict: false },
  { date: 1, muted: false, today: false, events: 1, recommended: false, conflict: false },
  { date: 2, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 3, muted: false, today: false, events: 2, recommended: false, conflict: false },
  { date: 4, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 5, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 6, muted: false, today: false, events: 1, recommended: false, conflict: false },
  { date: 7, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 8, muted: false, today: true, events: 2, recommended: false, conflict: false },
  { date: 9, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 10, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 11, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 12, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 13, muted: false, today: false, events: 1, recommended: false, conflict: false },
  { date: 14, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 15, muted: false, today: false, events: 0, recommended: false, conflict: false },
  { date: 16, muted: false, today: false, events: 1, recommended: false, conflict: false },
  { date: 17, muted: false, today: false, events: 0, recommended: false, conflict: false },
]);

onMounted(async () => {
  try {
    const appRows = await fetchApplications();
    applications.value = appRows;
    
    // Parse query parameter applicationId
    const queryAppId = Number(route.query.applicationId);
    if (queryAppId && appRows.some(a => a.id === queryAppId)) {
      selectedApplicationId.value = queryAppId;
    } else if (appRows.length > 0) {
      selectedApplicationId.value = appRows[0].id;
    }
  } catch (err) {
    console.error('Failed to load candidate applications:', err);
  } finally {
    loading.value = false;
  }
});

async function generateSchedule() {
  if (generating.value) return;
  generating.value = true;
  try {
    const result = await generateInterviewSchedule(buildSchedulePayload());
    if (result.status === 'algorithm_not_ready') {
      throw new Error('schedule unavailable');
    }
    applyScheduleResult(result);
    scheduleNotice.value = '';
    emit('show-toast', '已生成智能排期建议。');
  } catch {
    applyLocalSuggestion();
    scheduleNotice.value = '智能排期暂时无法获取，已显示本地排期建议。';
    emit('show-toast', '智能排期暂时无法获取，已显示本地排期建议。');
  } finally {
    generating.value = false;
  }
}

function buildSchedulePayload(): SchedulePreviewRequest {
  const currentAppId = selectedApplicationId.value || 1;
  const currentApp = applications.value.find(a => a.id === currentAppId);
  
  return {
    application_id: currentAppId,
    candidate: {
      candidate_id: currentApp?.candidate_id || 1,
      available_slots: [
        { start: '2026-07-10T09:30:00', end: '2026-07-10T12:00:00' },
        { start: '2026-07-16T14:00:00', end: '2026-07-16T17:00:00' },
      ],
    },
    interviewers: [
      {
        interviewer_id: 11,
        employee_name: '王刚',
        specialties: ['算法', '数据平台'],
        available_slots: [{ start: '2026-07-10T09:00:00', end: '2026-07-10T11:30:00' }],
      },
      {
        interviewer_id: 12,
        employee_name: '林雨晴',
        specialties: ['前端工程'],
        available_slots: [{ start: '2026-07-16T14:30:00', end: '2026-07-16T16:30:00' }],
      },
    ],
    meeting_rooms: [
      {
        meeting_room_id: 21,
        room_name: '线上会议室 A',
        available_slots: [{ start: '2026-07-10T09:30:00', end: '2026-07-10T12:00:00' }],
      },
      {
        meeting_room_id: 22,
        room_name: '会议室 B-201',
        available_slots: [{ start: '2026-07-16T15:00:00', end: '2026-07-16T17:00:00' }],
      },
    ],
    duration_minutes: 60,
  };
}

function applyScheduleResult(result: SchedulePreviewResponse) {
  const start = String(result.recommended_time?.start || '2026-07-10T10:00:00');
  const end = String(result.recommended_time?.end || '2026-07-10T11:00:00');
  const startDate = new Date(start);
  const endDate = new Date(end);
  const timeLabel = `${formatClock(startDate)} - ${formatClock(endDate)}`;
  const score = Number(result.conflict_explanation?.priority_score ?? 90);

  const currentAppId = selectedApplicationId.value || 1;
  const currentApp = applications.value.find(a => a.id === currentAppId);
  const candidateName = currentApp?.candidate_name || 'Eleanor Vance';
  const roleName = currentApp?.job_title || '首席数据科学家';

  apiSuggestion.value = {
    time: `7 月 ${startDate.getDate()} 日 ${timeLabel}`,
    interviewerAvailability: result.interviewer_availability || '面试官在该时间段可用。',
    candidateAvailability: result.candidate_availability || '候选人在该时间段可用。',
    conflict: result.conflict_detection || '未发现冲突。',
    reason: result.recommendation_reason || '该时间段满足候选人、面试官 and 会议室可用条件。',
    score,
    hasConflict: Boolean(result.conflict_explanation?.conflicts && Array.isArray(result.conflict_explanation.conflicts) && result.conflict_explanation.conflicts.length),
  };

  scheduleGenerated.value = true;
  markCalendarDay(startDate.getDate(), apiSuggestion.value.hasConflict);
  scheduleItems.value = [
    {
      time: formatClock(startDate),
      duration: `${Math.max(30, Math.round((endDate.getTime() - startDate.getTime()) / 60000))} 分钟`,
      candidate: candidateName,
      role: roleName,
      interviewer: Number(result.recommended_interviewer_id) === 12 ? '林雨晴' : '王刚',
      room: Number(result.recommended_room_id) === 22 ? '会议室 B-201' : '线上会议室 A',
      status: '推荐时段',
      recommended: true,
      hasConflict: apiSuggestion.value.hasConflict,
    },
    ...scheduleItems.value.filter((item) => !item.recommended).slice(0, 2),
  ];
}

function applyLocalSuggestion() {
  activeSuggestionIndex.value = (activeSuggestionIndex.value + 1) % suggestions.value.length;
  scheduleGenerated.value = true;
  const suggestion = currentSuggestion.value;
  markCalendarDay(activeSuggestionIndex.value === 0 ? 10 : 16, suggestion.hasConflict);
  scheduleItems.value = [
    {
      time: activeSuggestionIndex.value === 0 ? '10:00' : '15:00',
      duration: activeSuggestionIndex.value === 0 ? '60 分钟' : '45 分钟',
      candidate: activeSuggestionIndex.value === 0 ? 'Eleanor Vance' : 'Michael Chen',
      role: activeSuggestionIndex.value === 0 ? '首席数据科学家' : '高级前端工程师',
      interviewer: activeSuggestionIndex.value === 0 ? '王刚' : '林雨晴',
      room: activeSuggestionIndex.value === 0 ? '线上会议室 A' : '会议室 B-201',
      status: suggestion.hasConflict ? '需复核' : '推荐时段',
      recommended: true,
      hasConflict: suggestion.hasConflict,
    },
    ...scheduleItems.value.filter((item) => !item.recommended).slice(0, 2),
  ];
}

function markCalendarDay(date: number, hasConflict: boolean) {
  calendarDays.value = calendarDays.value.map((day) => ({
    ...day,
    recommended: day.date === date ? true : day.recommended,
    conflict: day.date === date ? hasConflict : day.conflict,
  }));
}

function formatClock(value: Date) {
  return value.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });
}
</script>
