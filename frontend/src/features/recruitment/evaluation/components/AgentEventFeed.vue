<template>
  <section class="event-feed">
    <header><div><span>真实 SSE</span><h2>实时事件</h2></div><strong>{{ streaming ? '已连接' : '未连接' }}</strong></header>
    <div class="event-feed__notes"><p>当前策略规划阶段未调用业务 Tool</p><p>当前策略规划阶段尚未进入企业知识检索</p></div>
    <div v-if="events.length" class="event-feed__list">
      <article v-for="event in events" :key="event.event_id">
        <div><time>{{ formatTime(event.created_at) }}</time><strong>{{ event.display_name }}</strong><span>{{ event.event_type }} · {{ event.status }}</span></div>
        <pre>{{ formatSummary(event.summary) }}</pre>
        <small>耗时：{{ event.duration_ms === null ? '—' : `${event.duration_ms} ms` }}</small>
        <p v-if="event.error" class="event-feed__error">{{ event.error.code }}：{{ event.error.message }}</p>
      </article>
    </div>
    <div v-else class="event-feed__empty">尚未收到运行事件。</div>
  </section>
</template>

<script setup lang="ts">
import type { AgentEvent } from '../../../../shared/agent/contracts';
defineProps<{ events:AgentEvent[]; streaming:boolean }>();
const formatTime=(value:string)=>new Date(value).toLocaleTimeString('zh-CN',{hour12:false});
const formatSummary=(summary:Record<string,unknown>)=>JSON.stringify(summary,null,2);
</script>

<style scoped>
.event-feed { display:grid; min-height:520px; max-height:720px; grid-template-rows:auto auto 1fr; gap:14px; padding:22px; border:1px solid var(--color-line); border-radius:var(--radius-md); background:#fff; box-shadow:var(--shadow-card); }.event-feed header { display:flex; align-items:flex-end; justify-content:space-between; }.event-feed header span { color:var(--color-primary); font-size:12px; font-weight:800; }.event-feed h2 { margin:5px 0 0; }.event-feed header strong { color:var(--color-muted); font-size:12px; }.event-feed__notes { display:grid; grid-template-columns:1fr 1fr; gap:8px; }.event-feed__notes p { margin:0; padding:9px; border-radius:10px; background:var(--color-surface-soft); color:var(--color-muted); font-size:12px; }.event-feed__list { display:grid; align-content:start; gap:10px; overflow:auto; padding-right:4px; }.event-feed article { padding:12px; border:1px solid var(--color-line); border-radius:12px; }.event-feed article>div { display:grid; grid-template-columns:auto 1fr auto; gap:10px; align-items:center; }.event-feed time,.event-feed article span,.event-feed small { color:var(--color-subtle); font-size:11px; }.event-feed pre { overflow:auto; margin:10px 0; padding:10px; border-radius:8px; background:#f8fafc; color:#334155; font:12px/1.5 ui-monospace,monospace; white-space:pre-wrap; }.event-feed__empty { display:grid; place-items:center; color:var(--color-muted); }.event-feed__error { color:#b91c1c; } @media(max-width:700px){.event-feed__notes{grid-template-columns:1fr}.event-feed article>div{grid-template-columns:1fr}}
</style>

