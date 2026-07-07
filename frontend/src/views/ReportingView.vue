<template>
  <div class="space-y-4 max-w-container-max mx-auto w-full h-full">
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-4">
      <div>
        <h2 class="font-display text-[28px] font-bold text-on-background mb-1">数据报表与智能分析</h2>
        <p class="font-body-md text-body-md text-on-surface-variant">TalentOS AI 实时生成的人才趋势和漏斗转化报告。</p>
      </div>
      <div class="flex gap-3 flex-shrink-0">
        <button class="whitespace-nowrap flex-shrink-0 px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg text-primary font-medium hover:bg-surface-container-low transition-colors flex items-center gap-2 text-sm shadow-sm">
          <span class="material-symbols-outlined text-[18px]">calendar_month</span>
          最近 30 天
        </button>
        <button class="whitespace-nowrap flex-shrink-0 px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg text-primary font-medium hover:bg-surface-container-low transition-colors flex items-center gap-2 text-sm shadow-sm">
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
            <h3 class="font-display text-[32px] font-bold text-on-surface leading-none">12,450</h3>
            <div class="flex items-center text-sm font-medium text-emerald-600 gap-1">
              <span class="material-symbols-outlined text-[14px]">trending_up</span> 14%
            </div>
          </div>
        </div>
        <p class="text-xs text-outline">较上月增加 1,520 人</p>
      </div>

      <div class="col-span-1 md:col-span-3 glass-card rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div>
          <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mb-1">本月入职人数</p>
          <div class="flex items-end gap-2 mb-2">
            <h3 class="font-display text-[32px] font-bold text-on-surface leading-none">342</h3>
            <div class="flex items-center text-sm font-medium text-emerald-600 gap-1">
              <span class="material-symbols-outlined text-[14px]">trending_up</span> 5%
            </div>
          </div>
        </div>
        <p class="text-xs text-outline">完成季度目标 85%</p>
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
              本月 <strong>工程部</strong> 招聘周期（38天）超出均值，主要瓶颈在 <strong>“技术面试”</strong> 环节。
              建议：增加外部技术面试官，或启用 TalentOS 代码评估机器人进行初筛，预计可缩短 5-7 天周期。
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
          <div>
            <div class="flex justify-between text-sm mb-1"><span class="font-medium">工程研发部</span><span>85% (34/40)</span></div>
            <div class="w-full bg-surface-container-highest rounded-full h-2.5">
              <div class="bg-primary h-2.5 rounded-full" style="width: 85%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1"><span class="font-medium">销售与市场部</span><span>92% (110/120)</span></div>
            <div class="w-full bg-surface-container-highest rounded-full h-2.5">
              <div class="bg-primary-container h-2.5 rounded-full" style="width: 92%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1"><span class="font-medium">运营部</span><span>60% (30/50)</span></div>
            <div class="w-full bg-surface-container-highest rounded-full h-2.5">
              <div class="bg-[#f59e0b] h-2.5 rounded-full" style="width: 60%"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Funnel Analysis -->
      <div class="col-span-1 md:col-span-4 glass-card rounded-xl p-5 shadow-sm flex flex-col justify-between">
        <div>
          <h3 class="font-title-lg text-title-lg font-semibold mb-4 text-lg">招聘漏斗 (Conversion Funnel)</h3>
          <div class="flex flex-col gap-3.5">
            <!-- Layer 1 -->
            <div class="w-full">
              <div class="flex justify-between items-center text-xs font-semibold mb-1 text-on-surface">
                <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-primary/40 flex-shrink-0"></span> 简历获取</span>
                <span class="font-bold text-sm">12,450 <span class="text-outline font-normal text-xs ml-1">100%</span></span>
              </div>
              <div class="w-full h-2.5 bg-surface-container-high rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full" style="width: 100%"></div>
              </div>
            </div>
            <!-- Layer 2 -->
            <div class="w-full">
              <div class="flex justify-between items-center text-xs font-semibold mb-1 text-on-surface">
                <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-primary/60 flex-shrink-0"></span> 简历筛选</span>
                <span class="font-bold text-sm">4,120 <span class="text-primary bg-primary/10 px-1.5 py-0.5 rounded text-[10px] ml-1 font-bold">33%</span></span>
              </div>
              <div class="w-full h-2.5 bg-surface-container-high rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full" style="width: 33%"></div>
              </div>
            </div>
            <!-- Layer 3 -->
            <div class="w-full">
              <div class="flex justify-between items-center text-xs font-semibold mb-1 text-on-surface">
                <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-primary/80 flex-shrink-0"></span> 面试阶段</span>
                <span class="font-bold text-sm">1,250 <span class="text-primary bg-primary/10 px-1.5 py-0.5 rounded text-[10px] ml-1 font-bold">10%</span></span>
              </div>
              <div class="w-full h-2.5 bg-surface-container-high rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full" style="width: 10%"></div>
              </div>
            </div>
            <!-- Layer 4 -->
            <div class="w-full">
              <div class="flex justify-between items-center text-xs font-semibold mb-1 text-on-surface">
                <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-primary flex-shrink-0"></span> 录用意向</span>
                <span class="font-bold text-sm">410 <span class="text-primary bg-primary/10 px-1.5 py-0.5 rounded text-[10px] ml-1 font-bold">3.3%</span></span>
              </div>
              <div class="w-full h-2.5 bg-surface-container-high rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full" style="width: 3.3%"></div>
              </div>
            </div>
            <!-- Layer 5 -->
            <div class="w-full">
              <div class="flex justify-between items-center text-xs font-semibold mb-1 text-on-surface">
                <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-primary-fixed flex-shrink-0"></span> 正式入职</span>
                <span class="font-bold text-sm">342 <span class="text-primary bg-primary/10 px-1.5 py-0.5 rounded text-[10px] ml-1 font-bold">2.7%</span></span>
              </div>
              <div class="w-full h-2.5 bg-surface-container-high rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full" style="width: 2.7%"></div>
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
            <h3 class="font-title-lg text-title-lg font-semibold mb-1 text-lg">平均招聘周期趋势</h3>
            <p class="text-xs text-on-surface-variant">月度趋势数据监控，当前均值：<strong class="text-on-surface">32天</strong></p>
          </div>
          <div class="flex items-center gap-1.5 bg-surface-container-low px-2 py-1 rounded-full text-xs text-on-surface-variant">
            <span class="w-1.5 h-1.5 rounded-full bg-primary-container"></span> 目标: < 35 天
          </div>
        </div>
        <div class="w-full flex-1 min-h-[250px]">
          <v-chart class="chart" :option="lineOptions" autoresize />
        </div>
      </div>
    </div>

    <!-- Bottom CTA -->
    <div class="mt-4 flex justify-end pb-8">
      <button class="bg-gradient-to-r from-primary-container to-tertiary-container text-on-primary px-6 py-3 rounded-xl font-body-md font-semibold hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-2 ai-glow text-sm">
        <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
        生成月度智能分析报告 (Generate AI Report)
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, LineChart } from 'echarts/charts';
import { TooltipComponent, GridComponent, LegendComponent, MarkLineComponent } from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';
import { provide } from 'vue';

use([
  CanvasRenderer,
  PieChart,
  LineChart,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  MarkLineComponent
]);

// provide(THEME_KEY, 'dark');

const pieOptions = {
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
      data: [
        { value: 35, name: '内推', itemStyle: { color: '#1b4dff' } },
        { value: 25, name: '猎头', itemStyle: { color: '#4f51dc' } },
        { value: 20, name: '直招', itemStyle: { color: '#b9c3ff' } },
        { value: 20, name: '校园', itemStyle: { color: '#e0dfff' } }
      ]
    }
  ]
};

const lineOptions = {
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
    data: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月'],
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#747688', fontSize: 10 }
  },
  yAxis: {
    type: 'value',
    min: 20,
    max: 50,
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
      name: '周期(天)',
      type: 'line',
      data: [42, 39, 41, 37, 35, 33, 34, 32, 32],
      smooth: true,
      symbolSize: 8,
      itemStyle: { color: '#1b4dff' },
      lineStyle: { width: 3 },
      markLine: {
        data: [{ yAxis: 35 }],
        lineStyle: { type: 'dashed', color: '#747688' },
        label: { show: false }
      }
    }
  ]
};
</script>

<style scoped>
.chart {
  height: 100%;
  width: 100%;
}
</style>
