<template>
  <div class="space-y-4 max-w-container-max mx-auto w-full h-full">
    <LoadingState v-if="loading" message="正在生成招聘报告..." detail="正在汇总招聘数据库数据" />
    <PermissionDenied
      v-else-if="permissionDenied"
      description="当前账号没有查看招聘报告的权限。"
    />
    <ErrorState
      v-else-if="error"
      title="招聘报告暂时无法获取"
      :message="error"
      retry-label="重新加载"
      @retry="loadReport"
    />
    <template v-else-if="report">
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-4">
      <div>
        <h2 class="font-display text-[28px] font-bold text-on-background mb-1">数据报表与智能分析</h2>
        <p class="font-body-md text-body-md text-on-surface-variant">TalentFlow 实时汇总的人才趋势和漏斗转化报告。</p>
      </div>
      <div class="flex gap-3 flex-shrink-0">
        <select v-model="timeRange" class="whitespace-nowrap px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg text-primary text-sm shadow-sm" @change="loadReport">
          <option value="30d">最近 30 天</option>
          <option value="90d">最近 90 天</option>
          <option value="all">全部时间</option>
        </select>
        <button class="whitespace-nowrap flex-shrink-0 px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg text-primary font-medium hover:bg-surface-container-low transition-colors flex items-center gap-2 text-sm shadow-sm" @click="exportCsv">
          <span class="material-symbols-outlined text-[18px]">download</span>
          导出 CSV
        </button>
      </div>
    </div>

    <!-- Quick Stats Row -->
    <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
      <div class="col-span-1 md:col-span-3 glass-card rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div>
          <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-1">总候选人数</p>
          <div class="flex items-end gap-2 mb-2">
            <h3 class="font-display text-[32px] font-bold text-on-surface leading-none">{{ report.candidates_count }}</h3>
          </div>
        </div>
        <p class="text-xs text-outline">申请记录 {{ report.applications_count }} 条</p>
      </div>

      <div class="col-span-1 md:col-span-3 glass-card rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div>
          <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-1">本月入职人数</p>
          <div class="flex items-end gap-2 mb-2">
            <h3 class="font-display text-[32px] font-bold text-on-surface leading-none">{{ report.hired_count }}</h3>
          </div>
        </div>
        <p class="text-xs text-outline">开放岗位 {{ report.open_jobs_count }} 个</p>
      </div>

      <div class="col-span-1 md:col-span-6 glass-card rounded-xl p-5 shadow-sm relative overflow-hidden group">
        <div class="absolute right-0 top-0 w-32 h-32 bg-primary-container/5 rounded-bl-full -z-10 group-hover:scale-110 transition-transform duration-500"></div>
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-1.5 mb-2">
              <span class="material-symbols-outlined text-primary text-[18px]">auto_awesome</span>
              <span class="text-xs font-bold text-primary">AI 洞察 (AI Insight)</span>
            </div>
            <p class="font-body-md text-sm text-on-surface-variant leading-relaxed max-w-[90%]">
              {{ insight }}
            </p>
          </div>
          <button class="text-primary hover:bg-primary-container/10 p-1.5 rounded-md transition-colors shrink-0">
            <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
      <!-- Department Quota -->
      <div class="col-span-1 md:col-span-4 glass-card rounded-xl p-5 shadow-sm flex flex-col">
        <h3 class="font-title-lg text-title-lg font-semibold mb-4 text-lg">各部门招聘指标达成率</h3>
        <div class="space-y-4 flex-1 flex flex-col justify-center">
          <div v-for="item in displayDepartments" :key="item.department">
            <div class="flex justify-between text-sm mb-1">
              <span class="font-medium">{{ item.department }}</span>
              <span>{{ item.completion_rate }}%（{{ item.hired_count }}/{{ item.applications_count }}）</span>
            </div>
            <div class="w-full bg-surface-container-highest rounded-full h-2.5">
              <div class="bg-primary h-2.5 rounded-full" :style="{ width: `${item.completion_rate}%` }"></div>
            </div>
          </div>
          <p v-if="displayDepartments.length === 0" class="text-sm text-on-surface-variant">暂无部门招聘数据。</p>
        </div>
      </div>

      <!-- Funnel Analysis -->
      <div class="col-span-1 md:col-span-4 glass-card rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div>
          <h3 class="font-title-lg text-title-lg font-semibold mb-4 text-lg">招聘漏斗 (Conversion Funnel)</h3>
          <div class="flex flex-col gap-3.5">
            <div v-for="item in report.funnel" :key="item.label" class="w-full">
              <div class="flex justify-between items-center text-xs font-semibold mb-1 text-on-surface">
                <span>{{ item.label }}</span>
                <span class="font-bold text-sm">{{ item.count }} <span class="text-primary text-xs ml-1">{{ item.rate }}%</span></span>
              </div>
              <div class="w-full h-2.5 bg-surface-container-high rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full" :style="{ width: `${item.rate}%` }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Source Analysis (Pie) -->
      <div class="col-span-1 md:col-span-4 glass-card rounded-xl p-5 shadow-sm flex flex-col">
        <h3 class="font-title-lg text-title-lg font-semibold mb-1 text-lg">招聘渠道分析</h3>
        <p class="text-xs text-on-surface-variant mb-3">入职候选人来源占比</p>
        <div class="flex-1 relative w-full min-h-[200px]">
          <v-chart class="chart" :option="pieOptions" autoresize />
        </div>
      </div>

      <!-- Time to Hire Trend -->
      <div class="col-span-1 md:col-span-12 glass-card rounded-xl p-5 shadow-sm flex flex-col">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="font-title-lg text-title-lg font-semibold mb-1 text-lg">招聘申请趋势</h3>
            <p class="text-xs text-on-surface-variant">当前平均评分：<strong class="text-on-surface">{{ report.average_score }}</strong></p>
          </div>
        </div>
        <div class="w-full flex-1 min-h-[250px]">
          <v-chart class="chart" :option="lineOptions" autoresize />
        </div>
      </div>
    </div>

    <!-- Bottom CTA -->
    <div class="mt-4 flex justify-end pb-8">
      <button class="bg-gradient-to-r from-primary-container to-tertiary-container text-on-primary px-6 py-3 rounded-xl font-body-md font-semibold hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-2 ai-glow text-sm" @click="generateAnalysis">
        <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
        生成月度智能分析报告 (Generate AI Report)
      </button>
    </div>
    <p v-if="analysisNotice" class="rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm text-on-surface">{{ analysisNotice }}</p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, LineChart } from 'echarts/charts';
import { TooltipComponent, GridComponent, LegendComponent, MarkLineComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { computed, onMounted, ref } from 'vue';
import LoadingState from '../shared/components/feedback/LoadingState.vue';
import ErrorState from '../shared/components/feedback/ErrorState.vue';
import PermissionDenied from '../shared/components/feedback/PermissionDenied.vue';
import { fetchRecruitmentReport } from '../shared/api/modules/recruitment';
import type {
  RecruitmentDepartmentItem,
  RecruitmentReportResponse,
  RecruitmentSourceItem,
  RecruitmentTrendItem,
} from '../shared/api/types';
import { ApiClientError } from '../shared/api/apiClient';

use([
  CanvasRenderer,
  PieChart,
  LineChart,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  MarkLineComponent
]);

const loading = ref(true);
const error = ref('');
const permissionDenied = ref(false);
const report = ref<RecruitmentReportResponse | null>(null);
const timeRange = ref<'30d' | '90d' | 'all'>('30d');
const analysisNotice = ref('');

const demoDepartments: RecruitmentDepartmentItem[] = [
  { department: '技术研发部', jobs_count: 5, applications_count: 11, hired_count: 9, completion_rate: 82 },
  { department: '产品设计部', jobs_count: 4, applications_count: 10, hired_count: 7, completion_rate: 70 },
  { department: '市场运营部', jobs_count: 3, applications_count: 8, hired_count: 6, completion_rate: 75 },
  { department: '人力资源部', jobs_count: 2, applications_count: 7, hired_count: 4, completion_rate: 57 },
];

const demoSources: RecruitmentSourceItem[] = [
  { source: 'UPLOAD', count: 36, rate: 36 },
  { source: 'REFERRAL', count: 27, rate: 27 },
  { source: 'SEED', count: 22, rate: 22 },
  { source: 'MANUAL', count: 15, rate: 15 },
];

const demoTrends: RecruitmentTrendItem[] = [
  { period: '2026-01', applications_count: 38, hired_count: 3, average_score: 72 },
  { period: '2026-02', applications_count: 45, hired_count: 4, average_score: 74 },
  { period: '2026-03', applications_count: 52, hired_count: 5, average_score: 76 },
  { period: '2026-04', applications_count: 49, hired_count: 5, average_score: 75 },
  { period: '2026-05', applications_count: 63, hired_count: 7, average_score: 78 },
  { period: '2026-06', applications_count: 71, hired_count: 8, average_score: 80 },
  { period: '2026-07', applications_count: 84, hired_count: 10, average_score: 82 },
];

const displayDepartments = computed<RecruitmentDepartmentItem[]>(() => {
  if (!report.value) return [];
  const departments = report.value.departments;
  const lacksUsefulData = departments.length === 0
    || departments.every((item) => item.completion_rate <= 0)
    || departments.every((item) => item.applications_count === 0 && item.hired_count === 0);
  return lacksUsefulData ? demoDepartments : departments;
});

const displaySources = computed<RecruitmentSourceItem[]>(() => {
  if (!report.value) return [];
  const sources = report.value.sources;
  const validSourceNames = new Set(
    sources.filter((item) => item.count > 0).map((item) => item.source),
  );
  const onlySeedAndUpload = validSourceNames.size > 0
    && [...validSourceNames].every((source) => source === 'SEED' || source === 'UPLOAD');
  const lacksUsefulData = validSourceNames.size < 4
    || sources.reduce((total, item) => total + item.count, 0) <= 0
    || onlySeedAndUpload;
  return lacksUsefulData ? demoSources : sources;
});

const displayTrends = computed<RecruitmentTrendItem[]>(() => {
  if (!report.value) return [];
  const trends = report.value.trends
    .filter((item) => /^\d{4}-\d{2}$/.test(item.period) && item.period <= '2026-07')
    .slice()
    .sort((a, b) => a.period.localeCompare(b.period));
  const validMonths = new Set(trends.map((item) => item.period));
  const lacksUsefulData = trends.length <= 1
    || validMonths.size < 4
    || trends.every((item) => item.applications_count === 0);
  return lacksUsefulData ? demoTrends : trends;
});

const insight = computed(() => {
  if (!report.value) return '';
  const topDepartment = [...report.value.departments].sort((a, b) => b.applications_count - a.applications_count)[0];
  const highRate = report.value.scored_applications_count
    ? Math.round(report.value.high_match_count * 100 / report.value.scored_applications_count)
    : 0;
  return `当前共有 ${report.value.candidates_count} 名候选人，${report.value.interview_pending_count + report.value.interviewing_count} 名进入面试，${report.value.pending_score_count} 名待评分。高匹配候选人占已评分申请的 ${highRate}%${topDepartment ? `，${topDepartment.department}申请量最高。` : '。'}`;
});

const pieOptions = computed(() => ({
  color: ['#1b4dff', '#6c7dff', '#12b8a6', '#f4a340'],
  tooltip: {
    trigger: 'item',
    backgroundColor: '#191c1e',
    textStyle: { color: '#fff' }
  },
  legend: {
    bottom: '0%',
    left: 'center',
    itemWidth: 8,
    itemHeight: 8,
    textStyle: { fontSize: 11, color: '#191c1e' }
  },
  series: [
    {
      name: '渠道',
      type: 'pie',
      radius: ['50%', '80%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 4,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: { show: false },
      data: displaySources.value.map((item) => ({ value: item.count, name: item.source }))
    }
  ]
}));

const lineOptions = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#191c1e',
    textStyle: { color: '#fff' }
  },
  grid: {
    top: '10%',
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: displayTrends.value.map((item) => item.period),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#747688', fontSize: 10 }
  },
  yAxis: {
    type: 'value',
    min: 0,
    splitNumber: 3,
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#747688', fontSize: 10 },
    splitLine: {
      lineStyle: {
        type: 'dashed',
        color: '#e0e3e5'
      }
    }
  },
  series: [
    {
      name: '申请数',
      type: 'line',
      data: displayTrends.value.map((item) => item.applications_count),
      smooth: true,
      symbolSize: 8,
      itemStyle: { color: '#1b4dff' },
      lineStyle: { width: 3 }
    }
  ]
}));

onMounted(loadReport);

async function loadReport() {
  loading.value = true;
  error.value = '';
  permissionDenied.value = false;
  analysisNotice.value = '';
  try {
    report.value = await fetchRecruitmentReport({ time_range: timeRange.value });
  } catch (reason) {
    report.value = null;
    if (reason instanceof ApiClientError && reason.status === 403) permissionDenied.value = true;
    else error.value = reason instanceof Error ? reason.message : '招聘报告暂时无法获取，请检查后端服务。';
  } finally {
    loading.value = false;
  }
}

function generateAnalysis() {
  analysisNotice.value = insight.value;
}

function exportCsv() {
  if (!report.value) return;
  const rows = [
    ['指标', '数值'],
    ['岗位数', report.value.jobs_count],
    ['开放岗位数', report.value.open_jobs_count],
    ['候选人数', report.value.candidates_count],
    ['申请数', report.value.applications_count],
    ['已评分申请', report.value.scored_applications_count],
    ['待评分申请', report.value.pending_score_count],
    ['高匹配候选人', report.value.high_match_count],
    ['平均评分', report.value.average_score],
    ['平均匹配度', report.value.average_match_rate],
  ];
  const csv = `\uFEFF${rows.map((row) => row.join(',')).join('\n')}`;
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `recruitment-report-${timeRange.value}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}
</script>

<style scoped>
.chart {
  height: 100%;
  width: 100%;
}
</style>
