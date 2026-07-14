<template>
  <section class="event-feed" :class="{ 'event-feed--collapsed': collapsed }">
    <button type="button" class="event-feed__toggle" @click="collapsed = !collapsed">
      <div class="event-feed__heading">
        <span>真实 SSE</span>
        <h2>实时事件</h2>
      </div>
      <div class="event-feed__meta">
        <strong>{{ connectionLabel }}</strong>
        <svg class="event-feed__chevron" :class="{ 'event-feed__chevron--collapsed': collapsed }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
      </div>
    </button>
    <div v-if="!collapsed" class="event-feed__body">
      <div class="event-feed__notes"><p>无 Tool 事件时明确显示"未调用"</p><p>无来源事件时明确显示"未检索"</p></div>
      <div v-if="events.length" class="event-feed__list">
        <article
          v-for="event in events"
          :key="event.event_id"
          :class="{ 'event-feed__article--expanded': isExpanded(event.event_id) }"
        >
          <button
            type="button"
            class="event-feed__summary"
            @click="toggleEvent(event.event_id)"
          >
            <time>{{ formatTime(event.created_at) }}</time>
            <strong>{{ event.display_name }}</strong>
            <div class="event-feed__summary-right">
              <span>{{ event.event_type }} · {{ event.status }}</span>
              <svg class="event-feed__event-chevron" :class="{ 'event-feed__event-chevron--collapsed': !isExpanded(event.event_id) }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
            </div>
          </button>
          <div v-if="isExpanded(event.event_id)" class="event-feed__detail">
            <dl>
              <div><dt>Tool</dt><dd>{{ event.tool_name || '本事件未调用' }}</dd></div>
              <div><dt>来源</dt><dd>{{ event.source_count ? `${event.source_count} 个` : '本事件未检索' }}</dd></div>
              <div><dt>回退</dt><dd>{{ event.fallback_used ? '已使用' : '未使用' }}</dd></div>
              <div><dt>耗时</dt><dd>{{ event.duration_ms === null ? '—' : `${event.duration_ms} ms` }}</dd></div>
            </dl>
            <pre>{{ formatSummary(event.summary) }}</pre>
            <p v-if="event.error" class="event-feed__error">{{ formatError(event) }}</p>
          </div>
        </article>
      </div>
      <div v-else class="event-feed__empty">尚未收到运行事件。</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { AgentRunStatus, type AgentEvent } from '../../../../shared/agent/contracts';

const props = defineProps<{ events: AgentEvent[]; streaming: boolean; status?: AgentRunStatus }>();
const collapsed = ref(false);
const expandedEvents = reactive(new Set<string>());

function isExpanded(eventId: string): boolean { return expandedEvents.has(eventId); }
function toggleEvent(eventId: string): void {
  if (expandedEvents.has(eventId)) { expandedEvents.delete(eventId); }
  else { expandedEvents.add(eventId); }
}

const connectionLabel = computed(() => {
  if (props.streaming) return '已连接';
  if (props.status === AgentRunStatus.COMPLETED) return '已结束';
  if (props.status === AgentRunStatus.FAILED) return '运行失败';
  if (props.events.length) return '历史事件';
  return '未连接';
});
const formatTime = (value: string) => new Date(value).toLocaleTimeString('zh-CN', { hour12: false });
const formatSummary = (summary: Record<string, unknown>) => JSON.stringify(summary, null, 2);
function formatError(event: AgentEvent): string {
  if (!event.error) return '';
  const node = typeof event.error.details.failed_node === 'string' ? event.error.details.failed_node : event.node_name || '未知';
  const step = typeof event.error.details.failed_step === 'string' ? event.error.details.failed_step : '未知';
  return `${event.error.code}：${event.error.message}；节点：${node}；步骤：${step}`;
}
</script>

<style scoped>
.event-feed {
  display: grid;
  min-height: 520px;
  max-height: 760px;
  grid-template-rows: auto 1fr;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}
.event-feed__toggle {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  padding: 22px;
  border: none;
  background: none;
  color: inherit;
  cursor: pointer;
}
.event-feed__heading span {
  display: block;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 800;
  text-align: left;
}
.event-feed__heading h2 {
  margin: 5px 0 0;
  text-align: left;
}
.event-feed__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.event-feed__meta strong {
  color: var(--color-muted);
  font-size: 12px;
  white-space: nowrap;
}
.event-feed__chevron {
  color: var(--color-subtle);
  transition: transform 0.25s ease;
}
.event-feed__chevron--collapsed {
  transform: rotate(-90deg);
}
.event-feed--collapsed {
  min-height: auto;
  max-height: none;
}
.event-feed__body {
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 14px;
  padding: 14px 22px 22px;
  overflow: hidden;
}
.event-feed__notes {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.event-feed__notes p {
  margin: 0;
  padding: 9px;
  border-radius: 10px;
  background: var(--color-surface-soft);
  color: var(--color-muted);
  font-size: 12px;
}
.event-feed__list {
  display: grid;
  align-content: start;
  gap: 10px;
  overflow: auto;
  padding-right: 4px;
}
.event-feed article {
  padding: 12px;
  border: 1px solid var(--color-line);
  border-radius: 12px;
}
.event-feed__summary {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  align-items: center;
  width: 100%;
  padding: 0;
  border: none;
  background: none;
  color: inherit;
  cursor: pointer;
  text-align: inherit;
}
.event-feed__summary-right {
  display: flex;
  align-items: center;
  gap: 6px;
}
.event-feed__event-chevron {
  color: var(--color-subtle);
  transition: transform 0.25s ease;
}
.event-feed__event-chevron--collapsed {
  transform: rotate(-90deg);
}
.event-feed__article--expanded .event-feed__summary {
  margin-bottom: 10px;
}
.event-feed time,
.event-feed__summary span {
  color: var(--color-subtle);
  font-size: 11px;
}
.event-feed__detail dl {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 6px;
}
.event-feed__detail dl div {
  min-width: 0;
  padding: 7px;
  border-radius: 8px;
  background: var(--color-surface-soft);
}
.event-feed__detail dt {
  color: var(--color-subtle);
  font-size: 10px;
}
.event-feed__detail dd {
  overflow: hidden;
  margin: 3px 0 0;
  color: var(--color-muted);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.event-feed__detail pre {
  overflow: auto;
  margin: 10px 0 0;
  padding: 10px;
  border-radius: 8px;
  background: var(--color-surface-soft);
  color: var(--color-muted);
  font: 12px/1.5 ui-monospace, monospace;
  white-space: pre-wrap;
}
.event-feed__empty {
  display: grid;
  place-items: center;
  color: var(--color-muted);
}
.event-feed__error {
  color: var(--color-status-error-text);
  font-size: 12px;
}
@media (max-width: 700px) {
  .event-feed__notes,
  .event-feed__detail dl { grid-template-columns: 1fr 1fr; }
  .event-feed__summary { grid-template-columns: 1fr; }
}
</style>
