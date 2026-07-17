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
            v-if="canManageInterviews"
            class="flex items-center gap-2 px-5 py-3 bg-primary text-on-primary rounded-xl font-label-md font-semibold shadow-md hover:shadow-lg hover:bg-primary-fixed-dim hover:text-on-primary-fixed transition-all disabled:opacity-50 disabled:cursor-wait"
            :disabled="generating"
            @click="generateSchedule"
          >
            <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
            {{ generating ? `排期中 ${batchProgress.current}/${batchProgress.total}` : '智能排期' }}
          </button>
        </div>

        <div v-if="serviceError" class="flex items-center justify-between gap-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          <div>
            <strong class="block">{{ serviceErrorTitle }}</strong>
            <span>{{ serviceError }}</span>
          </div>
          <button class="rounded-lg bg-primary px-4 py-2 font-semibold text-white" @click="reloadInterviewData">
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
                <h2 class="font-display text-display text-on-surface mt-1">{{ todayInterviewItems.length }}</h2>
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
              <div>
                <h3 class="font-title-lg text-title-lg text-on-surface">{{ calendarTitle }}</h3>
                <div class="mt-2 flex gap-1">
                  <button class="rounded bg-surface-container-low px-2 py-1 text-xs" @click="moveCalendar(-1)">{{ calendarView === 'month' ? '上月' : '上周' }}</button>
                  <button class="rounded bg-surface-container-low px-2 py-1 text-xs" @click="goToday">今天</button>
                  <button class="rounded bg-surface-container-low px-2 py-1 text-xs" @click="moveCalendar(1)">{{ calendarView === 'month' ? '下月' : '下周' }}</button>
                </div>
              </div>
              <div class="flex bg-surface-container-low rounded-lg p-1">
                <button
                  class="px-3 py-1 rounded font-label-md text-label-md transition-colors"
                  :class="calendarView === 'month' ? 'bg-surface-container-lowest shadow-sm text-on-surface' : 'text-on-surface-variant hover:text-on-surface'"
                  @click="calendarView = 'month'"
                >月视图</button>
                <button
                  class="px-3 py-1 rounded font-label-md text-label-md transition-colors"
                  :class="calendarView === 'week' ? 'bg-surface-container-lowest shadow-sm text-on-surface' : 'text-on-surface-variant hover:text-on-surface'"
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
                :key="day.key"
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
                  <p class="font-body-md text-body-md text-on-surface text-sm">{{ batchSummary }}</p>
                  <p class="text-xs text-on-surface-variant">已选择 {{ selectedApplicationIds.length }} 名候选人、{{ selectedInterviewerIds.length }} 名面试官</p>
                  <button v-if="canManageInterviews" class="text-primary font-label-md text-label-md mt-1 hover:underline disabled:opacity-50" :disabled="generating" @click="generateSchedule">开始批量排期</button>
                </div>
              </div>
            </div>
          </div>

          <div class="lg:col-span-8 glass-card rounded-xl p-0 flex flex-col h-full overflow-hidden">
            <div class="p-6 border-b border-outline-variant flex justify-between items-center bg-surface/50">
              <h3 class="font-title-lg text-title-lg text-on-surface">近期与推荐日程</h3>
              <span
                class="px-3 py-1 rounded-lg font-label-md text-label-md"
                :class="scheduleGenerated ? 'bg-emerald-50 text-emerald-700' : 'bg-surface-container text-on-surface-variant'"
              >{{ scheduleGenerated ? '本次排期已保存' : '共 ' + scheduleItems.length + ' 场' }}</span>
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_440px] gap-0 flex-1 overflow-hidden">
              <div class="overflow-y-auto p-6 space-y-4">
                <EmptyState
                  v-if="scheduleItems.length === 0"
                  title="暂无近期日程"
                  description="未来 7 天没有已保存面试，可以点击上方智能排期按钮生成并保存日程。"
                />

                <div
                  v-for="item in scheduleItems"
                  :key="item.time + item.candidate"
                  class="border rounded-xl p-4 flex items-center gap-6 relative shadow-sm transition-colors"
                  :class="{
                    'border-primary/20 bg-primary/5': scheduleGenerated && item.recommended && !item.hasConflict,
                    'border-[#EA580C]/20 bg-[#FFF7ED]': item.hasConflict,
                    'border-outline-variant bg-surface-container-lowest hover:border-primary/50': !scheduleGenerated || (!item.recommended && !item.hasConflict),
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

              <aside class="border-l border-outline-variant bg-surface/40 p-6 space-y-5 overflow-y-auto">
                <div>
                  <p class="font-label-md text-label-md text-primary uppercase tracking-wider">智能排期</p>
                  <div class="flex items-center justify-between gap-3 mt-1">
                    <h3 class="font-title-lg text-title-lg text-on-surface">批量排期设置</h3>
                    <span class="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">
                      已选 {{ selectedApplicationIds.length }} 人
                    </span>
                  </div>
                </div>

                <section class="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-3">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <h4 class="font-semibold text-on-surface">待约面候选人</h4>
                      <p class="mt-0.5 text-xs text-on-surface-variant">勾选后填写每人的空闲时间</p>
                    </div>
                    <span class="text-xs font-semibold text-primary">{{ selectedApplicationIds.length }}/{{ applications.length }}</span>
                  </div>
                  <div v-if="applications.length" class="space-y-3">
                    <article v-for="application in applications" :key="application.id" class="rounded-lg border border-outline-variant bg-surface p-3">
                      <label class="flex cursor-pointer items-start gap-3" :class="{ 'cursor-not-allowed opacity-70': generating }">
                        <input
                          v-model="selectedApplicationIds"
                          type="checkbox"
                          :value="application.id"
                          :disabled="generating"
                          class="mt-1 h-4 w-4 accent-primary"
                          @change="onCandidateSelectionChange(application)"
                        >
                        <span class="min-w-0 flex-1">
                          <span class="block truncate font-semibold text-on-surface">{{ candidateName(application) }}</span>
                          <span class="block truncate text-xs text-on-surface-variant">{{ jobName(application) }}</span>
                        </span>
                        <span class="shrink-0 rounded-full bg-amber-50 px-2 py-1 text-[11px] font-semibold text-amber-800">待约面</span>
                      </label>
                      <div v-if="selectedApplicationIds.includes(application.id)" class="mt-3 space-y-3 border-t border-outline-variant pt-3">
                        <label class="block space-y-1">
                          <span class="text-xs font-semibold text-on-surface-variant">面试时长（分钟）</span>
                          <input
                            v-model.number="candidateDurationDrafts[application.id]"
                            type="number"
                            min="30"
                            max="240"
                            step="15"
                            :disabled="generating"
                            class="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-sm text-on-surface outline-none focus:border-primary disabled:cursor-not-allowed disabled:opacity-60"
                            @input="candidateDurationErrors[application.id] = ''"
                          >
                        </label>
                        <p v-if="candidateDurationErrors[application.id]" class="text-xs text-red-800">
                          {{ candidateDurationErrors[application.id] }}
                        </p>
                        <AvailabilityEditor
                          :slots="candidateAvailabilityDrafts[application.candidate_id] || []"
                          :disabled="generating"
                          :minimum-minutes="candidateDuration(application.id)"
                          :error="candidateErrors[application.candidate_id]"
                          @add="addCandidateSlot(application.candidate_id)"
                          @remove="removeCandidateSlot(application.candidate_id, $event)"
                        />
                      </div>
                    </article>
                  </div>
                  <p v-else class="rounded-lg bg-surface-container-low p-3 text-sm text-on-surface-variant">暂无待约面候选人</p>
                </section>

                <section class="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-3">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <h4 class="font-semibold text-on-surface">参与匹配的面试官</h4>
                      <p class="mt-0.5 text-xs text-on-surface-variant">算法只会使用本次勾选的面试官</p>
                    </div>
                    <span class="text-xs font-semibold text-primary">已选 {{ selectedInterviewerIds.length }}</span>
                  </div>
                  <div v-if="interviewerResources.length" class="space-y-3">
                    <article v-for="interviewer in interviewerResources" :key="interviewer.id" class="rounded-lg border border-outline-variant bg-surface p-3">
                      <label class="flex cursor-pointer items-start gap-3" :class="{ 'cursor-not-allowed opacity-70': generating }">
                        <input
                          v-model="selectedInterviewerIds"
                          type="checkbox"
                          :value="interviewer.id"
                          :disabled="generating"
                          class="mt-1 h-4 w-4 accent-primary"
                          @change="onInterviewerSelectionChange(interviewer.id)"
                        >
                        <span class="min-w-0 flex-1">
                          <span class="block truncate font-semibold text-on-surface">{{ interviewerName(interviewer.id) }}</span>
                          <span class="block text-xs text-on-surface-variant">专长：{{ interviewerSpecialties(interviewer) }}</span>
                        </span>
                        <span class="shrink-0 rounded bg-surface-container px-2 py-1 text-[11px] font-semibold text-on-surface-variant">#{{ interviewer.id }}</span>
                      </label>
                      <AvailabilityEditor
                        v-if="selectedInterviewerIds.includes(interviewer.id)"
                        class="mt-3 border-t border-outline-variant pt-3"
                        :slots="interviewerAvailabilityDrafts[interviewer.id] || []"
                        :disabled="generating"
                        :minimum-minutes="maximumSelectedDuration"
                        :error="interviewerErrors[interviewer.id]"
                        @add="addInterviewerSlot(interviewer.id)"
                        @remove="removeInterviewerSlot(interviewer.id, $event)"
                      />
                    </article>
                  </div>
                  <p v-else class="rounded-lg bg-surface-container-low p-3 text-sm text-on-surface-variant">暂无启用的面试官资源</p>
                </section>

                <p v-if="!roomResources.length" class="rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
                  当前没有启用的会议室资源，无法开始智能排期。
                </p>

                <section v-if="batchResults.length" class="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-3">
                  <div class="flex items-center justify-between gap-3">
                    <h4 class="font-semibold text-on-surface">本次排期结果</h4>
                    <span class="text-xs font-semibold text-on-surface-variant">{{ batchSummary }}</span>
                  </div>
                  <div class="space-y-2">
                    <div v-for="result in batchResults" :key="result.applicationId" class="rounded-lg border border-outline-variant bg-surface p-3 text-sm">
                      <div class="flex items-start justify-between gap-3">
                        <div class="min-w-0">
                          <p class="truncate font-semibold text-on-surface">{{ result.candidateName }} · {{ result.jobName }}</p>
                          <p class="mt-1 text-xs text-on-surface-variant">{{ result.message }}</p>
                          <p v-if="result.status === 'success'" class="mt-1 text-xs text-on-surface-variant">
                            {{ formatResultTime(result) }} · {{ result.interviewerName }} · {{ result.roomName }}
                          </p>
                        </div>
                        <span class="shrink-0 rounded-full px-2 py-1 text-[11px] font-semibold" :class="batchStatusClass(result.status)">
                          {{ batchStatusLabel(result.status) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </section>

                <div class="space-y-2">
                  <button
                    v-if="canManageInterviews"
                    class="w-full rounded-lg bg-primary px-4 py-3 font-semibold text-white transition-colors hover:bg-primary-fixed-dim disabled:cursor-wait disabled:opacity-50"
                    :disabled="generating"
                    @click="generateSchedule"
                  >
                    {{ generating ? `排期中 ${batchProgress.current}/${batchProgress.total}` : '智能排期并保存' }}
                  </button>
                  <p class="text-xs leading-5 text-on-surface-variant">
                    智能排期将依次为所选候选人生成建议并保存面试安排。
                  </p>
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
import AvailabilityEditor from '../shared/components/interview/AvailabilityEditor.vue';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import EmptyState from '../shared/components/feedback/EmptyState.vue';
import PermissionDenied from '../shared/components/feedback/PermissionDenied.vue';
import {
  confirmInterviewSchedule,
  fetchInterviews,
  fetchInterviewers,
  fetchMeetingRooms,
  generateInterviewSchedule,
  saveInterviewAvailability,
  type InterviewerResource,
  type MeetingRoomResource,
} from '../shared/api/modules/interview';
import { fetchApplications, fetchCandidates, fetchJobs } from '../shared/api/modules/recruitment';
import type { CandidateApplicationListItem } from '../shared/api/modules/recruitment';
import type {
  Candidate as ApiCandidate,
  ConfirmInterviewScheduleRequest,
  InterviewAvailabilityBatchWrite,
  Job as ApiJob,
  SchedulePreviewResponse,
} from '../shared/api/types';
import { checkBackendHealth } from '../shared/api/modules/health';
import { ApiClientError } from '../shared/api/apiClient';
import { useAuthStore } from '../features/auth/authStore';

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

type BatchScheduleStatus = 'pending' | 'processing' | 'success' | 'failed';

type AvailabilitySlotDraft = {
  start: string;
  end: string;
};

type BatchScheduleResult = {
  applicationId: number;
  candidateName: string;
  jobName: string;
  status: BatchScheduleStatus;
  message: string;
  interviewerName?: string;
  roomName?: string;
  startAt?: string;
  endAt?: string;
};

type LoadOptions = {
  preserveSchedulingFeedback?: boolean;
};

const DEFAULT_INTERVIEW_DURATION_MINUTES = 60;
const MIN_INTERVIEW_DURATION_MINUTES = 30;
const MAX_INTERVIEW_DURATION_MINUTES = 240;
const route = useRoute();
const { hasPermission } = useAuthStore();
const emit = defineEmits<{
  'show-toast': [message: string];
}>();

const applications = ref<CandidateApplicationListItem[]>([]);
const selectedApplicationIds = ref<number[]>([]);
const selectedInterviewerIds = ref<number[]>([]);
const candidateDurationDrafts = ref<Record<number, number>>({});
const candidateAvailabilityDrafts = ref<Record<number, AvailabilitySlotDraft[]>>({});
const interviewerAvailabilityDrafts = ref<Record<number, AvailabilitySlotDraft[]>>({});
const candidateErrors = ref<Record<number, string>>({});
const candidateDurationErrors = ref<Record<number, string>>({});
const interviewerErrors = ref<Record<number, string>>({});
const candidates = ref<ApiCandidate[]>([]);
const jobs = ref<ApiJob[]>([]);
const interviewerResources = ref<InterviewerResource[]>([]);
const roomResources = ref<MeetingRoomResource[]>([]);
const interviewRecords = ref<Awaited<ReturnType<typeof fetchInterviews>>>([]);
const scheduleItems = ref<ScheduleItem[]>([]);
const batchResults = ref<BatchScheduleResult[]>([]);
const batchProgress = ref({ current: 0, total: 0 });
const loading = ref(true);
const permissionDenied = ref(false);
const generating = ref(false);
const calendarView = ref<'month' | 'week'>('month');
const viewDate = ref(new Date());
const scheduleNotice = ref('');
const serviceError = ref('');
const serviceErrorStatus = ref<number | undefined>();

const canManageInterviews = computed(() => hasPermission('interview.manage'));
const scheduleGenerated = computed(() => batchResults.value.some((item) => item.status === 'success'));
const maximumSelectedDuration = computed(() => {
  const durations = orderedSelectedApplications().map((application) => candidateDuration(application.id));
  return durations.length ? Math.max(...durations) : DEFAULT_INTERVIEW_DURATION_MINUTES;
});
const serviceErrorTitle = computed(() => serviceErrorStatus.value ? '面试数据加载失败。' : '无法连接后端服务。');
const weekdays = ['一', '二', '三', '四', '五', '六', '日'];
const todayInterviewItems = computed(() => {
  const today = formatDateKey(new Date());
  return interviewRecords.value.filter((item) => formatDateKey(new Date(item.start_at)) === today);
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
const batchSummary = computed(() => {
  if (!batchResults.value.length) return '等待开始批量排期';
  const success = batchResults.value.filter((item) => item.status === 'success').length;
  const failed = batchResults.value.filter((item) => item.status === 'failed').length;
  const processing = batchResults.value.some((item) => item.status === 'processing');
  return processing ? `正在处理第 ${batchProgress.value.current}/${batchProgress.value.total} 人` : `排期完成：成功 ${success} 人，失败 ${failed} 人`;
});
const calendarTitle = computed(() => `${viewDate.value.getFullYear()} 年 ${viewDate.value.getMonth() + 1} 月`);
const calendarDays = computed(() => buildCalendarDays(interviewRecords.value));

onMounted(() => {
  void loadInterviewData();
});

async function loadInterviewData(options: LoadOptions = {}) {
  loading.value = true;
  serviceError.value = '';
  permissionDenied.value = false;
  serviceErrorStatus.value = undefined;
  if (!options.preserveSchedulingFeedback) scheduleNotice.value = '';
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
    const pendingApplications = appRows.filter((item) => item.current_stage === 'INTERVIEW_PENDING');
    applications.value = pendingApplications;
    candidates.value = candidateRows;
    jobs.value = jobRows;
    interviewerResources.value = interviewerRows;
    roomResources.value = roomRows;
    interviewRecords.value = interviewRows;
    selectedApplicationIds.value = selectedApplicationIds.value.filter((id) => pendingApplications.some((item) => item.id === id));
    selectedInterviewerIds.value = selectedInterviewerIds.value.filter((id) => interviewerRows.some((item) => item.id === id));
    applyUpcomingScheduleItems(interviewRows, appRows);

    if (!options.preserveSchedulingFeedback) {
      applyApplicationQuerySelection(pendingApplications);
    }
  } catch (error) {
    applications.value = [];
    candidates.value = [];
    jobs.value = [];
    interviewerResources.value = [];
    roomResources.value = [];
    interviewRecords.value = [];
    scheduleItems.value = [];
    if (error instanceof ApiClientError && error.status === 403) {
      permissionDenied.value = true;
    } else {
      serviceErrorStatus.value = error instanceof ApiClientError ? error.status : undefined;
      serviceError.value = error instanceof Error ? error.message : '网络连接失败，服务端未响应。';
    }
  } finally {
    loading.value = false;
  }
}

function reloadInterviewData() {
  if (generating.value) return;
  batchResults.value = [];
  void loadInterviewData();
}

function applyApplicationQuerySelection(pendingApplications: CandidateApplicationListItem[]) {
  const queryValue = route.query.application_id;
  if (queryValue === undefined) return;
  const queryAppId = Number(Array.isArray(queryValue) ? queryValue[0] : queryValue);
  const application = pendingApplications.find((item) => item.id === queryAppId);
  if (!application) {
    scheduleNotice.value = '链接中的候选人申请不存在或不属于待约面阶段，未自动勾选。';
    return;
  }
  selectedApplicationIds.value = [application.id];
  ensureCandidateConfiguration(application);
}

function applyUpcomingScheduleItems(
  interviewRows: Awaited<ReturnType<typeof fetchInterviews>>,
  appRows: CandidateApplicationListItem[],
) {
  const todayStart = new Date();
  todayStart.setHours(0, 0, 0, 0);
  const upcomingEnd = new Date(todayStart);
  upcomingEnd.setDate(upcomingEnd.getDate() + 7);
  scheduleItems.value = interviewRows
    .filter((interview) => {
      const start = new Date(interview.start_at);
      return start >= todayStart && start < upcomingEnd;
    })
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
}

function onCandidateSelectionChange(application: CandidateApplicationListItem) {
  if (selectedApplicationIds.value.includes(application.id)) ensureCandidateConfiguration(application);
  delete candidateErrors.value[application.candidate_id];
  delete candidateDurationErrors.value[application.id];
  batchResults.value = [];
}

function onInterviewerSelectionChange(interviewerId: number) {
  if (selectedInterviewerIds.value.includes(interviewerId)) ensureInterviewerDraft(interviewerId);
  delete interviewerErrors.value[interviewerId];
  batchResults.value = [];
}

function ensureCandidateDraft(candidateId: number) {
  if (!candidateAvailabilityDrafts.value[candidateId]) {
    candidateAvailabilityDrafts.value[candidateId] = [emptyAvailabilitySlot()];
  }
}

function ensureCandidateConfiguration(application: CandidateApplicationListItem) {
  ensureCandidateDraft(application.candidate_id);
  if (candidateDurationDrafts.value[application.id] === undefined) {
    candidateDurationDrafts.value[application.id] = DEFAULT_INTERVIEW_DURATION_MINUTES;
  }
}

function candidateDuration(applicationId: number): number {
  const value = Number(candidateDurationDrafts.value[applicationId]);
  return Number.isInteger(value)
    && value >= MIN_INTERVIEW_DURATION_MINUTES
    && value <= MAX_INTERVIEW_DURATION_MINUTES
    ? value
    : DEFAULT_INTERVIEW_DURATION_MINUTES;
}

function ensureInterviewerDraft(interviewerId: number) {
  if (!interviewerAvailabilityDrafts.value[interviewerId]) {
    interviewerAvailabilityDrafts.value[interviewerId] = [emptyAvailabilitySlot()];
  }
}

function emptyAvailabilitySlot(): AvailabilitySlotDraft {
  return { start: '', end: '' };
}

function addCandidateSlot(candidateId: number) {
  ensureCandidateDraft(candidateId);
  candidateAvailabilityDrafts.value[candidateId].push(emptyAvailabilitySlot());
  delete candidateErrors.value[candidateId];
}

function removeCandidateSlot(candidateId: number, index: number) {
  candidateAvailabilityDrafts.value[candidateId]?.splice(index, 1);
  delete candidateErrors.value[candidateId];
}

function addInterviewerSlot(interviewerId: number) {
  ensureInterviewerDraft(interviewerId);
  interviewerAvailabilityDrafts.value[interviewerId].push(emptyAvailabilitySlot());
  delete interviewerErrors.value[interviewerId];
}

function removeInterviewerSlot(interviewerId: number, index: number) {
  interviewerAvailabilityDrafts.value[interviewerId]?.splice(index, 1);
  delete interviewerErrors.value[interviewerId];
}

async function generateSchedule() {
  if (generating.value) return;
  const selectedApplications = orderedSelectedApplications();
  const availabilityPayload = validateAndBuildAvailabilityPayload(selectedApplications);
  if (!availabilityPayload) return;

  const interviewerIds = orderedSelectedInterviewerIds();
  batchResults.value = selectedApplications.map((application) => ({
    applicationId: application.id,
    candidateName: candidateName(application),
    jobName: jobName(application),
    status: 'pending',
    message: '等待排期',
  }));
  batchProgress.value = { current: 0, total: selectedApplications.length };
  scheduleNotice.value = '';
  generating.value = true;

  try {
    await saveInterviewAvailability(availabilityPayload);
  } catch (error) {
    const message = errorMessage(error, '空闲时间保存失败。');
    batchResults.value.forEach((item) => {
      item.status = 'failed';
      item.message = `空闲时间保存失败，未开始排期：${message}`;
    });
    scheduleNotice.value = `空闲时间保存失败：${message}`;
    emit('show-toast', scheduleNotice.value);
    generating.value = false;
    return;
  }

  for (let index = 0; index < selectedApplications.length; index += 1) {
    const application = selectedApplications[index];
    const batchResult = batchResults.value[index];
    batchProgress.value.current = index + 1;
    batchResult.status = 'processing';
    batchResult.message = '正在生成并保存排期';
    try {
      const preview = await generateInterviewSchedule({
        application_id: application.id,
        duration_minutes: candidateDuration(application.id),
        interviewer_ids: interviewerIds,
      });
      const failureMessage = scheduleFailureMessage(preview);
      if (failureMessage) throw new Error(failureMessage);
      const confirmation = buildConfirmationPayload(application.id, preview, interviewerIds);
      await confirmInterviewSchedule(confirmation);
      batchResult.status = 'success';
      batchResult.message = preview.message || '排期建议已保存。';
      batchResult.interviewerName = interviewerName(confirmation.interviewer_id);
      batchResult.roomName = roomName(confirmation.meeting_room_id);
      batchResult.startAt = confirmation.start_at;
      batchResult.endAt = confirmation.end_at;
      if (!batchResults.value.slice(0, index).some((item) => item.status === 'success')) {
        viewDate.value = new Date(confirmation.start_at);
      }
    } catch (error) {
      batchResult.status = 'failed';
      batchResult.message = errorMessage(error, '该候选人排期失败。');
    }
  }

  const successCount = batchResults.value.filter((item) => item.status === 'success').length;
  const failedCount = batchResults.value.filter((item) => item.status === 'failed').length;
  scheduleNotice.value = `排期完成：成功 ${successCount} 人，失败 ${failedCount} 人`;
  emit('show-toast', scheduleNotice.value);
  await loadInterviewData({ preserveSchedulingFeedback: true });
  generating.value = false;
}

function orderedSelectedApplications(): CandidateApplicationListItem[] {
  const selected = new Set(selectedApplicationIds.value);
  return applications.value.filter((application) => selected.has(application.id));
}

function orderedSelectedInterviewerIds(): number[] {
  const selected = new Set(selectedInterviewerIds.value);
  return interviewerResources.value.filter((interviewer) => selected.has(interviewer.id)).map((interviewer) => interviewer.id);
}

function validateAndBuildAvailabilityPayload(
  selectedApplications: CandidateApplicationListItem[],
): InterviewAvailabilityBatchWrite | null {
  candidateErrors.value = {};
  candidateDurationErrors.value = {};
  interviewerErrors.value = {};
  if (!applications.value.length) {
    scheduleNotice.value = '暂无待约面候选人。';
    return null;
  }
  if (!selectedApplications.length) {
    scheduleNotice.value = '请至少选择一名待约面候选人。';
    return null;
  }
  if (!interviewerResources.value.length) {
    scheduleNotice.value = '暂无启用的面试官资源。';
    return null;
  }
  const interviewerIds = orderedSelectedInterviewerIds();
  if (!interviewerIds.length) {
    scheduleNotice.value = '请至少选择一名面试官。';
    return null;
  }
  if (!roomResources.value.length) {
    scheduleNotice.value = '暂无启用的会议室资源，无法开始排期。';
    return null;
  }

  let hasError = false;
  const durationByCandidate = new Map<number, number>();
  for (const application of selectedApplications) {
    const duration = Number(candidateDurationDrafts.value[application.id]);
    if (!Number.isInteger(duration)
        || duration < MIN_INTERVIEW_DURATION_MINUTES
        || duration > MAX_INTERVIEW_DURATION_MINUTES) {
      candidateDurationErrors.value[application.id] = `面试时长必须是 ${MIN_INTERVIEW_DURATION_MINUTES}–${MAX_INTERVIEW_DURATION_MINUTES} 之间的整数分钟。`;
      hasError = true;
      continue;
    }
    durationByCandidate.set(
      application.candidate_id,
      Math.max(durationByCandidate.get(application.candidate_id) || 0, duration),
    );
  }

  const candidatesPayload = new Map<number, InterviewAvailabilityBatchWrite['candidates'][number]>();
  for (const application of selectedApplications) {
    if (candidatesPayload.has(application.candidate_id)) continue;
    const requiredMinutes = durationByCandidate.get(application.candidate_id);
    if (!requiredMinutes) continue;
    const result = validateAvailabilitySlots(
      candidateAvailabilityDrafts.value[application.candidate_id] || [],
      requiredMinutes,
    );
    if (result.error) {
      candidateErrors.value[application.candidate_id] = result.error;
      hasError = true;
    } else {
      candidatesPayload.set(application.candidate_id, {
        candidate_id: application.candidate_id,
        duration_minutes: requiredMinutes,
        slots: result.slots,
      });
    }
  }

  const interviewersPayload: InterviewAvailabilityBatchWrite['interviewers'] = [];
  const selectedDurations = [...durationByCandidate.values()];
  const interviewerMinimumMinutes = selectedDurations.length
    ? Math.max(...selectedDurations)
    : DEFAULT_INTERVIEW_DURATION_MINUTES;
  for (const interviewerId of interviewerIds) {
    const result = validateAvailabilitySlots(
      interviewerAvailabilityDrafts.value[interviewerId] || [],
      interviewerMinimumMinutes,
    );
    if (result.error) {
      interviewerErrors.value[interviewerId] = result.error;
      hasError = true;
    } else {
      interviewersPayload.push({ interviewer_id: interviewerId, slots: result.slots });
    }
  }
  if (hasError) {
    scheduleNotice.value = '部分空闲时间填写有误，请按资源旁的提示修正后重试。';
    return null;
  }
  return { candidates: [...candidatesPayload.values()], interviewers: interviewersPayload };
}

function validateAvailabilitySlots(drafts: AvailabilitySlotDraft[], minimumMinutes: number): {
  slots: Array<{ start_at: string; end_at: string }>;
  error?: string;
} {
  if (!drafts.length) return { slots: [], error: '请至少添加一组空闲时间。' };
  const parsed: Array<{ start: Date; end: Date }> = [];
  for (const draft of drafts) {
    if (!draft.start || !draft.end) return { slots: [], error: '开始时间和结束时间不能为空。' };
    const start = new Date(draft.start);
    const end = new Date(draft.end);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return { slots: [], error: '时间格式无效，请重新填写。' };
    if (end <= start) return { slots: [], error: '结束时间必须晚于开始时间。' };
    if (start <= new Date()) return { slots: [], error: '空闲时间必须位于未来。' };
    if (end.getTime() - start.getTime() < minimumMinutes * 60_000) {
      return { slots: [], error: `每组空闲时间不得少于 ${minimumMinutes} 分钟。` };
    }
    parsed.push({ start, end });
  }
  parsed.sort((left, right) => left.start.getTime() - right.start.getTime());
  for (let index = 1; index < parsed.length; index += 1) {
    if (parsed[index].start < parsed[index - 1].end) return { slots: [], error: '同一资源的空闲时间不能重复或重叠。' };
  }
  return {
    slots: parsed.map((slot) => ({ start_at: slot.start.toISOString(), end_at: slot.end.toISOString() })),
  };
}

function scheduleFailureMessage(result: SchedulePreviewResponse): string {
  const backendMessage = String(result.message || '').trim();
  switch (result.status) {
    case 'candidate_availability_missing':
      return backendMessage || '该候选人没有有效的空闲时间。';
    case 'interviewer_availability_missing':
      return backendMessage || '所选面试官没有有效的空闲时间。';
    case 'room_availability_missing':
      return backendMessage || '会议室没有有效的空闲时间。';
    case 'no_available_slot':
      return backendMessage || '候选人、所选面试官和会议室没有满足 60 分钟的共同时间。';
    case 'algorithm_not_ready':
      return backendMessage || '智能排期服务暂不可用。';
    default:
      return result.recommended_time ? '' : (backendMessage || '暂时没有可用排期建议。');
  }
}

function buildConfirmationPayload(
  applicationId: number,
  preview: SchedulePreviewResponse,
  selectedInterviewers: number[],
): ConfirmInterviewScheduleRequest {
  const interviewerId = Number(preview.recommended_interviewer_id);
  const roomId = Number(preview.recommended_room_id);
  const startAt = String(preview.recommended_time?.start || '');
  const endAt = String(preview.recommended_time?.end || '');
  if (!Number.isInteger(interviewerId) || !selectedInterviewers.includes(interviewerId)) {
    throw new Error('排期建议返回了本次未选择的面试官。');
  }
  if (!Number.isInteger(roomId) || !roomResources.value.some((room) => room.id === roomId)) {
    throw new Error('排期建议缺少有效的会议室。');
  }
  const start = new Date(startAt);
  const end = new Date(endAt);
  if (!startAt || !endAt || Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end <= start) {
    throw new Error('排期建议缺少完整有效的开始时间或结束时间。');
  }
  if (preview.conflict_explanation?.recommended_slot_conflict === true) {
    throw new Error('排期建议存在资源冲突，未保存该候选人的面试安排。');
  }
  return {
    application_id: applicationId,
    interviewer_id: interviewerId,
    meeting_room_id: roomId,
    start_at: startAt,
    end_at: endAt,
    conflict_explanation: preview.conflict_explanation || {},
  };
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
  return String(interviewer?.employee_name || '').trim() || `面试官 #${interviewerId || '-'}`;
}

function interviewerSpecialties(interviewer: InterviewerResource): string {
  return interviewer.specialties?.map(String).filter(Boolean).join('、') || '暂未填写';
}

function roomName(roomId?: number | null): string {
  const room = roomResources.value.find((item) => item.id === Number(roomId));
  if (!room) return '会议室信息缺失';
  const name = String(room.name || '').trim() || '未命名会议室';
  const location = String(room.location || '').trim();
  return location ? `${name} · ${location}` : name;
}

function batchStatusLabel(status: BatchScheduleStatus): string {
  return { pending: '等待排期', processing: '正在排期', success: '排期成功', failed: '排期失败' }[status];
}

function batchStatusClass(status: BatchScheduleStatus): string {
  return {
    pending: 'bg-surface-container text-on-surface-variant',
    processing: 'bg-primary/10 text-primary',
    success: 'bg-emerald-100 text-emerald-700',
    failed: 'bg-red-50 text-red-800',
  }[status];
}

function formatResultTime(result: BatchScheduleResult): string {
  if (!result.startAt || !result.endAt) return '';
  const start = new Date(result.startAt);
  const end = new Date(result.endAt);
  return `${start.toLocaleDateString('zh-CN')} ${formatClock(start)} - ${formatClock(end)}`;
}

function errorMessage(error: unknown, fallback: string): string {
  return error instanceof Error && error.message ? error.message : fallback;
}

function buildCalendarDays(interviews: Array<{ start_at: string }>) {
  const now = new Date();
  const year = viewDate.value.getFullYear();
  const month = viewDate.value.getMonth();
  const first = calendarView.value === 'month'
    ? new Date(year, month, 1)
    : new Date(viewDate.value.getFullYear(), viewDate.value.getMonth(), viewDate.value.getDate());
  const startOffset = (first.getDay() + 6) % 7;
  const gridStart = new Date(first);
  gridStart.setDate(first.getDate() - startOffset);
  const counts = new Map<string, number>();
  for (const interview of interviews) {
    const value = new Date(interview.start_at);
    if (Number.isNaN(value.getTime())) continue;
    const key = formatDateKey(value);
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  const successfulDates = new Set(
    batchResults.value
      .filter((item) => item.status === 'success' && item.startAt)
      .map((item) => formatDateKey(new Date(item.startAt as string))),
  );
  const length = calendarView.value === 'month' ? 42 : 7;
  return Array.from({ length }, (_, index) => {
    const value = new Date(gridStart);
    value.setDate(gridStart.getDate() + index);
    const key = formatDateKey(value);
    return {
      key,
      date: value.getDate(),
      muted: calendarView.value === 'month' && value.getMonth() !== month,
      today: key === formatDateKey(now),
      events: counts.get(key) || 0,
      recommended: successfulDates.has(key),
      conflict: false,
    };
  });
}

function moveCalendar(direction: number) {
  const next = new Date(viewDate.value);
  if (calendarView.value === 'month') next.setMonth(next.getMonth() + direction, 1);
  else next.setDate(next.getDate() + direction * 7);
  viewDate.value = next;
}

function goToday() {
  viewDate.value = new Date();
}

function formatDateKey(value: Date) {
  return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`;
}

function formatClock(value: Date) {
  return value.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });
}
</script>

<style scoped>
/* 深色模式适配 */
[data-theme="dark"] .bg-red-50 { background-color: #450a0a !important; }
[data-theme="dark"] .text-red-800 { color: #fca5a5 !important; }
[data-theme="dark"] .bg-amber-50 { background-color: #451a03 !important; }
[data-theme="dark"] .text-amber-800 { color: #fdba74 !important; }
[data-theme="dark"] .bg-emerald-50 { background-color: #052e16 !important; }
[data-theme="dark"] .text-emerald-700 { color: #86efac !important; }
[data-theme="dark"] .bg-emerald-100 { background-color: #052e16 !important; }
[data-theme="dark"] .bg-\[\#FFF7ED\] { background-color: #451a03 !important; }
[data-theme="dark"] .bg-\[\#FFEDD5\] { background-color: #5c2d0a !important; }
[data-theme="dark"] .text-\[\#EA580C\] { color: #fdba74 !important; }
[data-theme="dark"] .border-\[\#EA580C\]\/20 { border-color: rgba(253, 186, 116, 0.2) !important; }
</style>
