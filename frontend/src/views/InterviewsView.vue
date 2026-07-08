<template>
  <div class="h-full flex flex-col bg-background">
    <!-- 加载态 -->
    <LoadingState
      v-if="loading"
      message="正在获取面试日程…"
      detail="连接排期服务中"
    />

    <!-- 权限拒绝 -->
    <PermissionDenied
      v-else-if="permissionDenied"
      description="你当前的角色无权访问面试日历，如需协助请联系 HR 管理员。"
    />

    <!-- 错误态 -->
    <ErrorState
      v-else-if="error"
      :message="error"
      retry-label="重新加载"
      @retry="retry"
    />

    <!-- 正常内容 -->
    <template v-else>
      <div class="max-w-container-max mx-auto space-y-gutter">
        <!-- Page Header -->
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
            {{ generating ? '排期中…' : '智能排期' }}
          </button>
        </div>

        <!-- Overview Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-gutter">
          <div class="glass-card rounded-xl p-6 relative overflow-hidden">
            <div class="absolute -right-4 -top-4 w-24 h-24 bg-primary-container/10 rounded-full blur-xl"></div>
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">今日面试总数</p>
                <h2 class="font-display text-display text-on-surface mt-1">{{ scheduleItems.length }}</h2>
              </div>
              <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">event</span>
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
                <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">rate_review</span>
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
                <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">timer</span>
              </div>
            </div>
            <div class="flex items-center gap-2 mt-4">
              <span class="material-symbols-outlined text-secondary text-[16px]">check_circle</span>
              <span class="font-label-md text-label-md text-on-surface-variant">符合标准预期时长</span>
            </div>
          </div>
        </div>

        <!-- Main Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-gutter min-h-[600px]">
          <!-- Left: Calendar -->
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

            <!-- Calendar Grid -->
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

            <!-- AI 排程建议 -->
            <div class="mt-4 pt-4 border-t border-outline-variant">
              <h4 class="font-label-md text-label-md text-on-surface-variant mb-2">AI 排程建议</h4>
              <div class="bg-surface-bright border border-primary/20 rounded-lg p-3 flex gap-3 items-start">
                <span class="material-symbols-outlined text-primary text-[20px]">smart_toy</span>
                <div>
                  <p class="font-body-md text-body-md text-on-surface text-sm">{{ currentSuggestion.reason }}</p>
                  <button class="text-primary font-label-md text-label-md mt-1 hover:underline" @click="generateSchedule">一键安排</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Interview List -->
          <div class="lg:col-span-8 glass-card rounded-xl p-0 flex flex-col h-full overflow-hidden">
            <div class="p-6 border-b border-outline-variant flex justify-between items-center bg-surface/50">
              <h3 class="font-title-lg text-title-lg text-on-surface">今日面试日程</h3>
              <div class="flex gap-2">
                <span
                  class="px-3 py-1 rounded-lg font-label-md text-label-md"
                  :class="scheduleGenerated ? 'bg-emerald-50 text-emerald-700' : 'bg-surface-container text-on-surface-variant'"
                >{{ scheduleGenerated ? '已生成排期建议' : '共 ' + scheduleItems.length + ' 场' }}</span>
              </div>
            </div>

            <div class="flex-1 overflow-y-auto p-6 space-y-4">
              <!-- 无日程空态 -->
              <EmptyState
                v-if="scheduleItems.length === 0"
                title="暂无今日日程"
                description="今天没有安排面试，可以点击上方「智能排期」按钮生成推荐日程。"
              />

              <!-- Interview Items -->
              <div
                v-for="item in scheduleItems"
                :key="item.time"
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
                  <div class="flex items-center gap-4 font-body-md text-body-md text-on-surface-variant text-sm">
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">person</span> 面试官: {{ item.interviewer }}</span>
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">{{ item.room.includes('线上') ? 'videocam' : 'location_on' }}</span> {{ item.room }}</span>
                  </div>
                </div>

                <div class="flex flex-col gap-2 shrink-0">
                  <button class="px-4 py-2 bg-white border border-outline-variant text-on-surface rounded-lg font-label-md text-label-md hover:bg-surface-container-low transition-colors">
                    查看简历
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- FAB -->
      <button class="fixed bottom-28 right-8 w-14 h-14 bg-primary text-on-primary rounded-full shadow-lg flex items-center justify-center hover:bg-primary-fixed-dim hover:text-on-primary-fixed hover:scale-105 transition-all duration-200 z-50">
        <span class="material-symbols-outlined text-3xl">add</span>
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import ErrorState from '../shared/components/feedback/ErrorState.vue';
import EmptyState from '../shared/components/feedback/EmptyState.vue';
import PermissionDenied from '../shared/components/feedback/PermissionDenied.vue';

const emit = defineEmits<{
  'show-toast': [message: string];
}>();

// ── 状态 ─────────────────────────────────────
const loading = ref(true);
const error = ref<string | null>(null);
const permissionDenied = ref(false);

const scheduleGenerated = ref(false);
const generating = ref(false);
const calendarView = ref<'month' | 'week'>('month');
const activeSuggestionIndex = ref(0);

// ── 数据 ─────────────────────────────────────
const weekdays = ['一', '二', '三', '四', '五', '六', '日'];

const scheduleItems = ref([
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

const suggestions = [
  {
    title: '优先安排 Eleanor Vance 技术终面',
    time: '7 月 10 日 10:00 - 11:00',
    interviewerAvailability: '王刚 09:30 - 11:30 可用',
    candidateAvailability: '候选人确认上午时段可参加',
    conflict: '未发现冲突',
    reason: '该候选人匹配度最高，且终面所需两位面试官在同一时间段均可用，建议优先安排。',
    hasConflict: false,
  },
  {
    title: '合并安排 Michael Chen 前端技术面',
    time: '7 月 16 日 15:00 - 15:45',
    interviewerAvailability: '林雨晴 14:30 - 16:00 可用',
    candidateAvailability: '候选人下午时段可用',
    conflict: '原 14:00 时段与会议室占用冲突',
    reason: '顺延后无需更换面试官，并能保留同一面试记录模板。',
    hasConflict: true,
  },
];

const currentSuggestion = computed(() => apiSuggestion.value ?? suggestions[activeSuggestionIndex.value]);

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

// ── 方法 ─────────────────────────────────────
function generateSchedule() {
  if (generating.value) return;
  generating.value = true;

  setTimeout(() => {
    scheduleGenerated.value = true;
    activeSuggestionIndex.value = (activeSuggestionIndex.value + 1) % suggestions.length;
    generating.value = false;

    // 更新日历日期
    const days = calendarDays.value;
    days[9].recommended = true;   // 7月10日
    days[15].recommended = true;  // 7月16日
    days[15].conflict = true;

    // 更新日程
    scheduleItems.value = [
      {
        time: '10:00',
        duration: '60 分钟',
        candidate: 'Eleanor Vance',
        role: '首席数据科学家',
        interviewer: '王刚',
        room: '线上会议室 A',
        status: '推荐时段',
        recommended: true,
        hasConflict: false,
      },
      {
        time: '14:00',
        duration: '45 分钟',
        candidate: 'Michael Chen',
        role: '高级前端工程师',
        interviewer: '林雨晴',
        room: '会议室 B-201',
        status: '可替换',
        recommended: false,
        hasConflict: true,
      },
      {
        time: '16:30',
        duration: '60 分钟',
        candidate: 'Sarah Jenkins',
        role: '产品经理',
        interviewer: '赵敏',
        room: '线上会议室 C',
        status: '新推荐',
        recommended: true,
        hasConflict: false,
      },
    ];

    emit('show-toast', '已生成智能排期建议，请注意查看冲突提醒。');
  }, 1200);
}

function retry() {
  loading.value = false;
  error.value = null;
  loading.value = true;
  setTimeout(() => { loading.value = false; }, 500);
}

onMounted(() => {
  setTimeout(() => { loading.value = false; }, 400);
});
</script>
