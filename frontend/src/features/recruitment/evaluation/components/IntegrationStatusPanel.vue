<template>
  <section class="integration-status" aria-live="polite">
    <header>
      <div><span>系统连接</span><h2>智能能力状态</h2></div>
      <button type="button" title="刷新集成状态" :disabled="loading" @click="$emit('refresh')">
        <RefreshCw :size="16" :class="{ 'is-spinning': loading }" />
      </button>
    </header>
    <p v-if="error" class="integration-status__error">集成状态暂时无法获取</p>
    <div v-else class="integration-status__grid">
      <article>
        <span>Run 存储</span>
        <strong>{{ health?.run_store.mode || '读取中' }}</strong>
      </article>
      <article>
        <span>LLM</span>
        <strong :class="modeClass(health?.integrations.llm.mode)">{{ health?.integrations.llm.mode || '读取中' }}</strong>
        <small>{{ health?.integrations.llm.model_name || health?.integrations.llm.provider || '—' }}</small>
      </article>
      <article>
        <span>RAG</span>
        <strong :class="modeClass(health?.integrations.rag.mode)">{{ health?.integrations.rag.mode || '读取中' }}</strong>
        <small>{{ health?.integrations.rag.collection_name || '—' }}</small>
      </article>
      <article>
        <span>知识库</span>
        <strong>{{ countLabel }}</strong>
        <small>文档 / Chunk</small>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RefreshCw } from 'lucide-vue-next';
import type { BackendHealth } from '../../../../shared/api/modules/health';

const props = defineProps<{
  health: BackendHealth | null;
  loading: boolean;
  error: string;
}>();

defineEmits<{ refresh: [] }>();

const countLabel = computed(() => {
  const rag = props.health?.integrations.rag;
  const documents = rag?.document_count;
  const chunks = rag?.chunk_count;
  return documents === null || documents === undefined || chunks === null || chunks === undefined
    ? '尚未统计'
    : `${documents} / ${chunks}`;
});

function modeClass(mode?: string): string {
  if (mode === 'READY' || mode === 'POSTGRESQL') return 'is-ready';
  if (mode === 'DISABLED') return 'is-disabled';
  return mode ? 'is-degraded' : '';
}
</script>

<style scoped>
.integration-status { display:grid; gap:14px; padding:18px 20px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:#fff; box-shadow:var(--shadow-card); }
.integration-status header { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.integration-status header span { color:var(--color-primary); font-size:11px; font-weight:800; }
.integration-status h2 { margin:4px 0 0; font-size:18px; }
.integration-status button { display:grid; width:36px; height:36px; place-items:center; border:1px solid var(--color-line); border-radius:6px; background:#fff; color:var(--color-muted); cursor:pointer; }
.integration-status button:disabled { cursor:default; opacity:.55; }
.integration-status__grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }
.integration-status article { min-width:0; padding:11px 12px; border-left:3px solid var(--color-line); background:var(--color-surface-soft); }
.integration-status article span,.integration-status article strong,.integration-status article small { display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.integration-status article span,.integration-status article small { color:var(--color-subtle); font-size:10px; }
.integration-status article strong { margin:5px 0; color:var(--color-text); font-size:13px; }
.integration-status__error { margin:0; padding:11px; background:#fff7ed; color:#9a3412; font-size:12px; }
.is-ready { color:#166534!important; }.is-disabled { color:#475569!important; }.is-degraded { color:#b45309!important; }
.is-spinning { animation:spin 1s linear infinite; } @keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:850px){.integration-status__grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:520px){.integration-status__grid{grid-template-columns:1fr}}
</style>
