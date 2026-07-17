<template>
  <div v-if="events.length" class="relative space-y-4 pl-7 before:absolute before:bottom-2 before:left-[9px] before:top-2 before:w-px before:bg-slate-200">
    <article v-for="event in events" :key="event.event_id" class="relative rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <span class="absolute -left-[26px] top-5 h-3 w-3 rounded-full border-2 border-white" :class="statusDotClass(event.status)"></span>
      <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <h4 class="text-sm font-bold text-slate-800">{{ event.display_name }}</h4>
            <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600">{{ event.event_type }}</span>
            <span class="rounded-full px-2 py-0.5 text-[10px] font-bold" :class="statusBadgeClass(event.status)">{{ event.status }}</span>
          </div>
          <p class="mt-1 text-xs text-slate-400">{{ formatDateTime(event.created_at) }}</p>
        </div>
        <div class="flex flex-wrap gap-2 text-[11px] text-slate-500">
          <span v-if="event.candidate_id !== null" class="rounded-lg bg-slate-50 px-2 py-1">{{ candidateLabel(event.candidate_id, candidateNames) }}</span>
          <span v-if="event.tool_name" class="rounded-lg bg-indigo-50 px-2 py-1 text-indigo-600">{{ toolLabel(event.tool_name) }}</span>
          <span v-if="event.duration_ms !== null" class="rounded-lg bg-slate-50 px-2 py-1">{{ event.duration_ms }} ms</span>
          <span v-if="event.source_count" class="rounded-lg bg-slate-50 px-2 py-1">{{ event.source_count }} 个来源</span>
          <span v-if="event.fallback_used" class="rounded-lg bg-amber-50 px-2 py-1 text-amber-700">使用回退模式</span>
        </div>
      </div>

      <dl v-if="formattedSummary(event).preferred.length" class="mt-3 grid gap-2 rounded-xl bg-slate-50/70 p-3 sm:grid-cols-2">
        <div v-for="item in formattedSummary(event).preferred" :key="item.key" class="min-w-0">
          <dt class="text-[11px] text-slate-400">{{ item.label }}</dt>
          <dd class="mt-0.5 break-words text-xs font-medium text-slate-700">{{ displayValue(item.value) }}</dd>
        </div>
      </dl>

      <div v-if="event.error" class="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">
        <p class="font-bold">{{ event.error.code }} · {{ event.error.message }}</p>
        <pre v-if="safeErrorDetails(event)" class="mt-2 overflow-x-auto whitespace-pre-wrap break-words font-mono text-[11px]">{{ safeErrorDetails(event) }}</pre>
      </div>

      <details v-if="hasExtraSummary(event)" class="mt-3 rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2">
        <summary class="cursor-pointer text-xs font-semibold text-slate-600">查看结构化摘要</summary>
        <pre class="mt-3 max-h-64 overflow-auto whitespace-pre-wrap break-words font-mono text-[11px] leading-5 text-slate-600">{{ extraSummaryJson(event) }}</pre>
      </details>
    </article>
  </div>
  <div v-else class="rounded-2xl border border-dashed border-slate-300 bg-slate-50/60 px-5 py-7 text-center text-sm text-slate-500">
    当前节点尚无执行事件。
  </div>
</template>

<script setup lang="ts">
import { AgentNodeStatus, type AgentEvent } from '../../../../shared/agent/contracts';
import {
  candidateLabel,
  formatEventSummary,
  isEmptyRecord,
  sanitizeStructuredValue,
  toolLabel,
} from '../utils/agentProcessingBasis';

defineProps<{
  events: AgentEvent[];
  candidateNames: Record<number, string>;
}>();

function formattedSummary(event: AgentEvent) {
  return formatEventSummary(event.summary);
}

function hasExtraSummary(event: AgentEvent): boolean {
  return !isEmptyRecord(formattedSummary(event).extra);
}

function extraSummaryJson(event: AgentEvent): string {
  return JSON.stringify(formattedSummary(event).extra, null, 2);
}

function safeErrorDetails(event: AgentEvent): string | null {
  if (!event.error || isEmptyRecord(event.error.details)) return null;
  const safeDetails = sanitizeStructuredValue(event.error.details);
  return safeDetails ? JSON.stringify(safeDetails, null, 2) : null;
}

function displayValue(value: unknown): string {
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (Array.isArray(value)) return value.map((item) => displayValue(item)).join('、') || '—';
  if (value && typeof value === 'object') return JSON.stringify(value);
  return value === null || value === undefined || value === '' ? '—' : String(value);
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('zh-CN', { hour12: false });
}

function statusDotClass(status: AgentNodeStatus): string {
  const classes: Record<AgentNodeStatus, string> = {
    [AgentNodeStatus.COMPLETED]: 'bg-emerald-500',
    [AgentNodeStatus.RUNNING]: 'bg-blue-500 animate-pulse',
    [AgentNodeStatus.NEEDS_REVIEW]: 'bg-amber-500',
    [AgentNodeStatus.FAILED]: 'bg-red-500',
    [AgentNodeStatus.SKIPPED]: 'bg-slate-400',
    [AgentNodeStatus.WAITING]: 'bg-slate-300',
  };
  return classes[status];
}

function statusBadgeClass(status: AgentNodeStatus): string {
  const classes: Record<AgentNodeStatus, string> = {
    [AgentNodeStatus.COMPLETED]: 'bg-emerald-50 text-emerald-700',
    [AgentNodeStatus.RUNNING]: 'bg-blue-50 text-blue-700',
    [AgentNodeStatus.NEEDS_REVIEW]: 'bg-amber-50 text-amber-700',
    [AgentNodeStatus.FAILED]: 'bg-red-50 text-red-700',
    [AgentNodeStatus.SKIPPED]: 'bg-slate-100 text-slate-600',
    [AgentNodeStatus.WAITING]: 'bg-slate-100 text-slate-500',
  };
  return classes[status];
}
</script>

<style scoped>
[data-theme="dark"] article,
[data-theme="dark"] .bg-white { background-color: #1e293b !important; }
[data-theme="dark"] .bg-slate-50,
[data-theme="dark"] .bg-slate-50\/70,
[data-theme="dark"] .bg-slate-50\/60,
[data-theme="dark"] .bg-slate-50\/50,
[data-theme="dark"] .bg-slate-100 { background-color: #334155 !important; }
[data-theme="dark"] .bg-indigo-50 { background-color: #1e1b4b !important; }
[data-theme="dark"] .bg-amber-50 { background-color: #451a03 !important; }
[data-theme="dark"] .bg-red-50 { background-color: #450a0a !important; }
[data-theme="dark"] .text-slate-800 { color: #e2e8f0 !important; }
[data-theme="dark"] .text-slate-700,
[data-theme="dark"] .text-slate-600 { color: #cbd5e1 !important; }
[data-theme="dark"] .text-slate-500,
[data-theme="dark"] .text-slate-400 { color: #94a3b8 !important; }
[data-theme="dark"] .text-indigo-600 { color: #a5b4fc !important; }
[data-theme="dark"] .border-slate-200,
[data-theme="dark"] .border-slate-300 { border-color: #475569 !important; }
[data-theme="dark"] .border-white { border-color: #1e293b !important; }
</style>
