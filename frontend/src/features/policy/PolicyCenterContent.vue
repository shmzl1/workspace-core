<template>
  <section class="policy-center">
    <header class="policy-center__header">
      <div>
        <h2>政策中心</h2>
        <p>浏览已发布的公司制度、员工福利及合规文档。</p>
      </div>
      <label class="policy-center__search">
        <span class="material-symbols-outlined">search</span>
        <input v-model="query" type="search" placeholder="搜索政策名称" @input="search" />
      </label>
    </header>

    <div class="policy-center__categories">
      <article v-for="item in overview.categories" :key="item.category" class="policy-center__category">
        <span class="material-symbols-outlined">folder_open</span>
        <strong>{{ item.category }}</strong>
        <small>{{ item.count }} 篇文档</small>
      </article>
    </div>

    <div class="policy-center__documents">
      <div class="policy-center__documents-header">
        <h3>核心文档</h3>
        <span v-if="loading">加载中…</span>
        <span v-else>{{ overview.documents.length }} 篇</span>
      </div>
      <p v-if="error" class="policy-center__error">{{ error }}</p>
      <p v-else-if="!loading && !overview.documents.length" class="policy-center__empty">暂无匹配的已发布政策。</p>
      <article v-for="document in overview.documents" :key="document.id" class="policy-center__document">
        <span class="material-symbols-outlined">description</span>
        <div>
          <h4>{{ document.title }}</h4>
          <p>{{ document.category }} · {{ document.version || '未标注版本' }} · 更新于 {{ formatDate(document.updated_at) }}</p>
          <small v-if="summary(document)">{{ summary(document) }}</small>
        </div>
        <a v-if="document.source_path" :href="document.source_path" class="policy-center__link">查看</a>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { fetchPolicies, type PolicyDocument, type PolicyOverview } from '../../shared/api/modules/policy';

const overview = ref<PolicyOverview>({ documents: [], categories: [] });
const loading = ref(false);
const error = ref('');
const query = ref('');
let timer: number | undefined;

const load = async () => {
  loading.value = true;
  error.value = '';
  try { overview.value = await fetchPolicies(query.value || undefined); }
  catch (err) { error.value = err instanceof Error ? err.message : '无法加载政策文档'; }
  finally { loading.value = false; }
};
const search = () => { window.clearTimeout(timer); timer = window.setTimeout(load, 250); };
const summary = (document: PolicyDocument) => typeof document.metadata_json.summary === 'string' ? document.metadata_json.summary : '';
const formatDate = (value: string) => new Date(value).toLocaleDateString('zh-CN');
onMounted(load);
</script>

<style scoped lang="scss">
.policy-center { max-width: 1080px; margin: 0 auto; padding-bottom: 48px; }
.policy-center__header { display: flex; justify-content: space-between; gap: 20px; align-items: flex-end; margin-bottom: 28px; }
.policy-center__header h2 { margin: 0; font-size: 30px; color: var(--color-text); }.policy-center__header p { color: var(--color-muted); }
.policy-center__search { display:flex; align-items:center; gap:8px; min-width:260px; padding:10px 12px; border:1px solid var(--color-line); border-radius:10px; background:var(--color-surface); }.policy-center__search input { border:0; outline:0; width:100%; }
.policy-center__categories { display:grid; grid-template-columns:repeat(auto-fit, minmax(190px, 1fr)); gap:14px; margin-bottom:22px; }.policy-center__category { display:grid; gap:5px; padding:18px; background:var(--color-surface); border:1px solid var(--color-line); border-radius:12px; }.policy-center__category span { color:var(--color-primary); }.policy-center__category small { color:var(--color-muted); }
.policy-center__documents { padding:20px; border:1px solid var(--color-line); border-radius:12px; background:var(--color-surface); }.policy-center__documents-header { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--color-line); }.policy-center__documents-header h3 { margin:0 0 14px; }.policy-center__documents-header span { color:var(--color-muted); font-size:13px; }
.policy-center__document { display:flex; align-items:flex-start; gap:14px; padding:16px 0; border-bottom:1px solid var(--color-line); }.policy-center__document:last-child { border-bottom:0; }.policy-center__document > span { color:var(--color-primary); }.policy-center__document div { flex:1; }.policy-center__document h4,.policy-center__document p,.policy-center__document small { margin:0; }.policy-center__document p,.policy-center__document small { color:var(--color-muted); font-size:13px; }.policy-center__document small { display:block; margin-top:5px; }.policy-center__link { color:var(--color-primary); font-weight:700; }.policy-center__error { color:#b42318; }.policy-center__empty { color:var(--color-muted); }
@media (max-width: 640px) { .policy-center__header { align-items:stretch; flex-direction:column; }.policy-center__search { min-width:0; } }
</style>
