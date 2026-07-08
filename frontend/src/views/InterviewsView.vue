<template>
  <div class="interviews-page">
    <section class="interviews-page__header">
      <div>
        <p>招聘流程</p>
        <h2>面试日历</h2>
        <span>统一管理候选人、面试官、会议室和时间槽。</span>
      </div>
      <button class="btn btn--primary" @click="generateSchedule">
        <span class="material-symbols-outlined">auto_awesome</span>
        智能排期
      </button>
    </section>

    <section class="interviews-page__metrics">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <span class="material-symbols-outlined">{{ metric.icon }}</span>
        <div>
          <strong>{{ metric.value }}</strong>
          <small>{{ metric.label }}</small>
        </div>
      </article>
    </section>

    <section class="interviews-page__grid">
      <div class="calendar-card">
        <div class="calendar-card__top">
          <div>
            <h3>2026 年 7 月</h3>
            <p>推荐日程会在日历中高亮展示。</p>
          </div>
          <div class="calendar-card__switch">
            <button class="active">月视图</button>
            <button>周视图</button>
          </div>
        </div>

        <div class="calendar-weekdays">
          <span v-for="day in weekdays" :key="day">{{ day }}</span>
        </div>

        <div class="calendar-grid">
          <button
            v-for="day in calendarDays"
            :key="day.date"
            class="calendar-day"
            :class="{
              'calendar-day--muted': day.muted,
              'calendar-day--today': day.today,
              'calendar-day--has-event': day.events > 0,
              'calendar-day--recommended': scheduleGenerated && day.recommended
            }"
          >
            <strong>{{ day.date }}</strong>
            <small v-if="day.events">{{ day.events }} 场</small>
            <span v-if="scheduleGenerated && day.recommended">推荐</span>
          </button>
        </div>
      </div>

      <div class="schedule-card">
        <div class="schedule-card__top">
          <div>
            <h3>今日面试日程</h3>
            <p>点击智能排期后会刷新推荐时间段。</p>
          </div>
          <button class="btn" @click="generateSchedule">
            <span class="material-symbols-outlined">refresh</span>
            刷新建议
          </button>
        </div>

        <div class="timeline">
          <article
            v-for="item in scheduleItems"
            :key="item.time"
            class="timeline-item"
            :class="{ 'timeline-item--recommended': scheduleGenerated && item.recommended }"
          >
            <div class="timeline-item__time">
              <strong>{{ item.time }}</strong>
              <span>{{ item.duration }}</span>
            </div>
            <div class="timeline-item__body">
              <div>
                <h4>{{ item.candidate }}</h4>
                <p>{{ item.role }}</p>
              </div>
              <div class="timeline-item__meta">
                <span><i class="material-symbols-outlined">person</i>{{ item.interviewer }}</span>
                <span><i class="material-symbols-outlined">meeting_room</i>{{ item.room }}</span>
              </div>
            </div>
            <em>{{ item.status }}</em>
          </article>
        </div>
      </div>
    </section>

    <section class="suggestion-panel">
      <div v-if="scheduleNotice" class="service-notice">
        <span class="material-symbols-outlined">info</span>
        <p>{{ scheduleNotice }}</p>
      </div>

      <div class="suggestion-panel__header">
        <div>
          <p>排期建议</p>
          <h3>{{ currentSuggestion.title }}</h3>
        </div>
        <span :class="scheduleGenerated ? 'status status--ready' : 'status'">
          {{ scheduleGenerated ? '已生成' : '待生成' }}
        </span>
      </div>

      <div class="suggestion-panel__grid">
        <article>
          <span class="material-symbols-outlined">schedule</span>
          <strong>推荐面试时间</strong>
          <p>{{ currentSuggestion.time }}</p>
        </article>
        <article>
          <span class="material-symbols-outlined">badge</span>
          <strong>面试官可用时间</strong>
          <p>{{ currentSuggestion.interviewerAvailability }}</p>
        </article>
        <article>
          <span class="material-symbols-outlined">person_check</span>
          <strong>候选人可用时间</strong>
          <p>{{ currentSuggestion.candidateAvailability }}</p>
        </article>
        <article>
          <span class="material-symbols-outlined">rule</span>
          <strong>冲突检测</strong>
          <p>{{ currentSuggestion.conflict }}</p>
        </article>
      </div>

      <div class="suggestion-panel__reason">
        <span class="material-symbols-outlined">psychology</span>
        <div>
          <strong>推荐理由</strong>
          <p>{{ currentSuggestion.reason }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { generateInterviewSchedule } from '../shared/api/modules';

const emit = defineEmits<{
  'show-toast': [message: string];
}>();

const scheduleGenerated = ref(false);
const activeSuggestionIndex = ref(0);
const scheduleNotice = ref('');
const apiSuggestion = ref<null | {
  title: string;
  time: string;
  interviewerAvailability: string;
  candidateAvailability: string;
  conflict: string;
  reason: string;
}>(null);

const metrics = [
  { label: '今日面试', value: '12', icon: 'event' },
  { label: '待评价面试', value: '4', icon: 'rate_review' },
  { label: '平均面试时长', value: '45 min', icon: 'timer' }
];

const weekdays = ['一', '二', '三', '四', '五', '六', '日'];

const calendarDays = [
  { date: 29, muted: true, today: false, events: 0, recommended: false },
  { date: 30, muted: true, today: false, events: 0, recommended: false },
  { date: 1, muted: false, today: false, events: 1, recommended: false },
  { date: 2, muted: false, today: false, events: 0, recommended: false },
  { date: 3, muted: false, today: false, events: 2, recommended: false },
  { date: 4, muted: false, today: false, events: 0, recommended: false },
  { date: 5, muted: false, today: false, events: 0, recommended: false },
  { date: 6, muted: false, today: false, events: 1, recommended: false },
  { date: 7, muted: false, today: false, events: 0, recommended: false },
  { date: 8, muted: false, today: true, events: 3, recommended: false },
  { date: 9, muted: false, today: false, events: 1, recommended: true },
  { date: 10, muted: false, today: false, events: 2, recommended: true },
  { date: 11, muted: false, today: false, events: 0, recommended: false },
  { date: 12, muted: false, today: false, events: 0, recommended: false },
  { date: 13, muted: false, today: false, events: 1, recommended: false },
  { date: 14, muted: false, today: false, events: 0, recommended: false },
  { date: 15, muted: false, today: false, events: 0, recommended: false },
  { date: 16, muted: false, today: false, events: 1, recommended: true },
  { date: 17, muted: false, today: false, events: 0, recommended: false },
  { date: 18, muted: false, today: false, events: 0, recommended: false },
  { date: 19, muted: false, today: false, events: 0, recommended: false }
];

const scheduleItems = computed(() => [
  {
    time: '10:00',
    duration: '60 分钟',
    candidate: 'Eleanor Vance',
    role: '首席数据科学家',
    interviewer: '王刚',
    room: '线上会议室 A',
    status: scheduleGenerated.value ? '推荐时段' : '已确认',
    recommended: true
  },
  {
    time: '14:00',
    duration: '45 分钟',
    candidate: 'Michael Chen',
    role: '高级前端工程师',
    interviewer: '林雨晴',
    room: '会议室 B-201',
    status: '待确认',
    recommended: false
  },
  {
    time: '16:30',
    duration: '60 分钟',
    candidate: 'Sarah Jenkins',
    role: '产品经理',
    interviewer: '赵敏',
    room: '线上会议室 C',
    status: scheduleGenerated.value ? '可替换' : '待协调',
    recommended: scheduleGenerated.value
  }
]);

const suggestions = [
  {
    title: '优先安排 Eleanor Vance 技术终面',
    time: '7 月 10 日 10:00 - 11:00',
    interviewerAvailability: '王刚 09:30 - 11:30 可用，技术负责人 10:00 - 11:00 可用。',
    candidateAvailability: '候选人确认上午时段可参加，远程面试优先。',
    conflict: '未发现会议室、面试官或候选人时间冲突。',
    reason: '该候选人匹配度最高，且终面所需两位面试官在同一时间段均可用。'
  },
  {
    title: '合并安排 Michael Chen 前端技术面',
    time: '7 月 16 日 15:00 - 15:45',
    interviewerAvailability: '林雨晴与前端负责人 14:30 - 16:00 可用。',
    candidateAvailability: '候选人下午时段可用，预计 6 周到岗。',
    conflict: '原 14:00 时段与会议室占用冲突，建议顺延至 15:00。',
    reason: '顺延后无需更换面试官，并能保留同一面试记录模板。'
  }
];

const currentSuggestion = computed(() => apiSuggestion.value ?? suggestions[activeSuggestionIndex.value]);

async function generateSchedule() {
  scheduleNotice.value = '';
  scheduleGenerated.value = true;
  try {
    const result = await generateInterviewSchedule({
      application_id: 1,
      candidate: {
        candidate_id: 1,
        available_slots: [
          { start: '2026-07-10T10:00:00', end: '2026-07-10T11:00:00' },
          { start: '2026-07-16T15:00:00', end: '2026-07-16T15:45:00' }
        ]
      },
      interviewers: [
        {
          interviewer_id: 1,
          employee_name: '王刚',
          specialties: ['技术终面', '数据科学'],
          available_slots: [{ start: '2026-07-10T09:30:00', end: '2026-07-10T11:30:00' }]
        }
      ],
      meeting_rooms: [
        {
          meeting_room_id: 1,
          room_name: '线上会议室 A',
          available_slots: [{ start: '2026-07-10T10:00:00', end: '2026-07-10T11:00:00' }]
        }
      ],
      duration_minutes: 60
    });

    if (result.status === 'algorithm_not_ready') {
      scheduleNotice.value = result.message;
      emit('show-toast', result.message);
      return;
    }

    apiSuggestion.value = {
      title: result.message || '智能排期建议',
      time: formatRecommendedTime(result.recommended_time),
      interviewerAvailability: result.interviewer_availability ?? '面试官可用时间已返回。',
      candidateAvailability: result.candidate_availability ?? '候选人可用时间已返回。',
      conflict: result.conflict_detection ?? JSON.stringify(result.conflict_explanation ?? {}),
      reason: result.recommendation_reason ?? '系统已根据候选人、面试官、会议室与时长约束生成建议。'
    };
    emit('show-toast', '已生成智能排期建议。');
  } catch {
    activeSuggestionIndex.value = (activeSuggestionIndex.value + 1) % suggestions.length;
    scheduleNotice.value = '智能排期服务暂时不可用，请稍后重试。';
    emit('show-toast', scheduleNotice.value);
  }
}

function formatRecommendedTime(value: Record<string, unknown> | null | undefined) {
  if (!value) return '推荐时间已返回。';
  const start = value.start ?? value.start_time;
  const end = value.end ?? value.end_time;
  if (start && end) return `${String(start)} - ${String(end)}`;
  return JSON.stringify(value);
}
</script>

<style scoped>
.interviews-page {
  display: grid;
  gap: 22px;
  max-width: 1440px;
  margin: 0 auto;
}

.interviews-page__header,
.interviews-page__metrics,
.interviews-page__grid,
.suggestion-panel {
  width: 100%;
}

.interviews-page__header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
}

.interviews-page__header p,
.suggestion-panel__header p {
  margin: 0 0 8px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 800;
}

.interviews-page__header h2,
.calendar-card__top h3,
.schedule-card__top h3,
.suggestion-panel__header h3 {
  margin: 0;
  color: var(--color-text);
}

.interviews-page__header h2 {
  font-size: 30px;
}

.interviews-page__header span,
.calendar-card__top p,
.schedule-card__top p {
  display: block;
  margin-top: 8px;
  color: var(--color-muted);
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
  transition: 0.2s ease;
}

.btn:hover {
  border-color: rgba(36, 85, 245, 0.35);
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

.interviews-page__metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.metric-card,
.calendar-card,
.schedule-card,
.suggestion-panel {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: #fff;
  box-shadow: var(--shadow-card);
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px;
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
  font-size: 24px;
}

.metric-card small {
  margin-top: 4px;
  color: var(--color-muted);
  font-weight: 700;
}

.interviews-page__grid {
  display: grid;
  grid-template-columns: minmax(360px, 0.9fr) minmax(0, 1.4fr);
  gap: 18px;
}

.calendar-card,
.schedule-card {
  padding: 20px;
}

.calendar-card__top,
.schedule-card__top,
.suggestion-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.calendar-card__switch {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border-radius: 12px;
  background: var(--color-surface-soft);
}

.calendar-card__switch button {
  min-height: 30px;
  padding: 0 10px;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: var(--color-muted);
  font-weight: 800;
}

.calendar-card__switch .active {
  background: #fff;
  color: var(--color-text);
  box-shadow: var(--shadow-card);
}

.calendar-weekdays,
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.calendar-weekdays span {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 800;
  text-align: center;
}

.calendar-grid {
  margin-top: 8px;
}

.calendar-day {
  display: grid;
  min-height: 70px;
  align-content: start;
  gap: 5px;
  padding: 9px;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  background: #fff;
  color: var(--color-text);
  text-align: left;
}

.calendar-day small,
.calendar-day span {
  color: var(--color-muted);
  font-size: 11px;
}

.calendar-day--muted {
  color: var(--color-subtle);
  background: var(--color-surface-soft);
}

.calendar-day--today {
  border-color: var(--color-primary);
  box-shadow: inset 0 0 0 1px var(--color-primary);
}

.calendar-day--has-event small {
  color: var(--color-primary);
  font-weight: 800;
}

.calendar-day--recommended {
  border-color: #16a34a;
  background: #f0fdf4;
}

.calendar-day--recommended span {
  width: max-content;
  padding: 2px 6px;
  border-radius: 999px;
  background: #dcfce7;
  color: #15803d;
  font-weight: 800;
}

.timeline {
  display: grid;
  gap: 12px;
}

.timeline-item {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr) 88px;
  gap: 16px;
  align-items: center;
  padding: 16px;
  border: 1px solid var(--color-line);
  border-radius: 14px;
  background: #fff;
}

.timeline-item--recommended {
  border-color: rgba(22, 163, 74, 0.45);
  background: #f0fdf4;
}

.timeline-item__time strong,
.timeline-item__time span,
.timeline-item__body h4,
.timeline-item__body p {
  display: block;
  margin: 0;
}

.timeline-item__time strong {
  color: var(--color-primary);
  font-size: 22px;
}

.timeline-item__time span,
.timeline-item__body p,
.timeline-item__meta span {
  color: var(--color-muted);
  font-size: 13px;
}

.timeline-item__body h4 {
  color: var(--color-text);
}

.timeline-item__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
}

.timeline-item__meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.timeline-item__meta i {
  font-size: 16px;
}

.timeline-item em,
.status {
  justify-self: end;
  padding: 5px 9px;
  border-radius: 999px;
  background: var(--color-surface-soft);
  color: var(--color-muted);
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.timeline-item--recommended em,
.status--ready {
  background: #dcfce7;
  color: #15803d;
}

.suggestion-panel {
  padding: 20px;
}

.service-notice {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin-bottom: 16px;
  padding: 12px;
  border: 1px solid rgba(36, 85, 245, 0.18);
  border-radius: 12px;
  background: #f7f9ff;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
}

.service-notice span {
  color: var(--color-primary);
}

.service-notice p {
  margin: 0;
}

.suggestion-panel__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.suggestion-panel__grid article,
.suggestion-panel__reason {
  padding: 14px;
  border: 1px solid var(--color-line);
  border-radius: 14px;
  background: var(--color-surface-soft);
}

.suggestion-panel__grid span,
.suggestion-panel__reason span {
  color: var(--color-primary);
}

.suggestion-panel__grid strong,
.suggestion-panel__reason strong {
  display: block;
  margin-top: 6px;
  color: var(--color-text);
}

.suggestion-panel__grid p,
.suggestion-panel__reason p {
  margin: 7px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.55;
}

.suggestion-panel__reason {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.suggestion-panel__reason strong {
  margin-top: 0;
}

@media (max-width: 1120px) {
  .interviews-page__grid,
  .suggestion-panel__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .interviews-page__header,
  .calendar-card__top,
  .schedule-card__top,
  .suggestion-panel__header {
    flex-direction: column;
    align-items: stretch;
  }

  .interviews-page__metrics {
    grid-template-columns: 1fr;
  }

  .timeline-item {
    grid-template-columns: 1fr;
  }

  .timeline-item em {
    justify-self: start;
  }
}
</style>
