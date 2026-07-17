<template>
  <div v-if="sources.length" class="grid gap-3 lg:grid-cols-2">
    <article
      v-for="source in sources"
      :key="source.source_id"
      class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4"
    >
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <h4 class="truncate text-sm font-bold text-slate-800" :title="source.title">{{ source.title }}</h4>
          <p class="mt-1 break-all text-[11px] text-slate-400" :title="source.source_id">{{ source.source_id }}</p>
        </div>
        <span v-if="source.relevance !== null" class="shrink-0 rounded-full bg-indigo-50 px-2.5 py-1 text-[11px] font-bold text-indigo-600">
          相关度 {{ formatScore(source.relevance) }}
        </span>
      </div>
      <dl class="mt-3 grid grid-cols-2 gap-2 text-xs">
        <div><dt class="text-slate-400">文档类型</dt><dd class="mt-0.5 text-slate-700">{{ source.document_type || '—' }}</dd></div>
        <div><dt class="text-slate-400">部门</dt><dd class="mt-0.5 text-slate-700">{{ source.department || '—' }}</dd></div>
        <div><dt class="text-slate-400">岗位编码</dt><dd class="mt-0.5 text-slate-700">{{ source.job_code || '—' }}</dd></div>
        <div><dt class="text-slate-400">版本 / 生效日</dt><dd class="mt-0.5 text-slate-700">{{ source.version || '—' }} / {{ source.effective_date || source.effective_from || '—' }}</dd></div>
      </dl>
      <p v-if="source.excerpt" class="mt-3 rounded-xl border border-slate-200 bg-white p-3 text-xs leading-5 text-slate-600">
        {{ source.excerpt }}
      </p>
    </article>
  </div>
  <div v-else class="rounded-2xl border border-dashed border-slate-300 bg-slate-50/60 px-5 py-7 text-center text-sm text-slate-500">
    该 Agent 本次运行未引用企业知识文档。
  </div>
</template>

<script setup lang="ts">
import type { KnowledgeSourceReference } from '../../../../shared/agent/contracts';

defineProps<{ sources: KnowledgeSourceReference[] }>();

function formatScore(value: number): string {
  const normalized = value <= 1 ? value * 100 : value;
  return `${normalized.toFixed(0)}%`;
}
</script>

<style scoped>
[data-theme="dark"] article,
[data-theme="dark"] .bg-slate-50\/70,
[data-theme="dark"] .bg-slate-50\/60 { background-color: rgba(15, 23, 42, 0.72) !important; }
[data-theme="dark"] .bg-white { background-color: #1e293b !important; }
[data-theme="dark"] .bg-indigo-50 { background-color: #1e1b4b !important; }
[data-theme="dark"] .text-slate-800 { color: #e2e8f0 !important; }
[data-theme="dark"] .text-slate-700 { color: #cbd5e1 !important; }
[data-theme="dark"] .text-slate-600,
[data-theme="dark"] .text-slate-500 { color: #94a3b8 !important; }
[data-theme="dark"] .text-slate-400 { color: #64748b !important; }
[data-theme="dark"] .text-indigo-600 { color: #a5b4fc !important; }
[data-theme="dark"] .border-slate-200,
[data-theme="dark"] .border-slate-300 { border-color: #334155 !important; }
</style>
