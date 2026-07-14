<template>
  <section class="bg-white rounded-3xl shadow-sm border border-slate-200 p-8 space-y-6">
    <div class="flex items-center justify-between border-b border-slate-100 pb-4">
      <h2 class="text-lg font-bold flex items-center gap-2 text-slate-900">
        <div class="w-1.5 h-6 bg-indigo-500 rounded-full"></div>
        顶层工作流执行链路
      </h2>
      <div class="flex items-center gap-4 text-[10px] sm:text-[11px] font-bold tracking-wider text-slate-400 uppercase">
        <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></div> Completed</div>
        <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse"></div> Running</div>
        <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></div> Needs Review</div>
      </div>
    </div>

    <!-- Workflow Canvas -->
    <div class="w-full bg-slate-50/50 rounded-2xl py-10 px-6 flex justify-center items-center overflow-x-auto no-scrollbar">
      <div class="flex items-center min-w-max space-x-1.5">
        
        <!-- Node 1: Strategy -->
        <div 
          @click="emit('select', 'recruitment_strategy')"
          :class="[
            'w-40 h-28 rounded-2xl shadow-sm flex flex-col items-center justify-center relative transition-all duration-300 cursor-pointer transform hover:-translate-y-1',
            selectedNode === 'recruitment_strategy' ? 'ring-2 ring-blue-500 ring-offset-2 scale-105' : '',
            nodeStyle(nodeMap.recruitment_strategy.status).cardClass
          ]"
        >
          <div :class="['w-10 h-10 rounded-full flex items-center justify-center mb-2', nodeStyle(nodeMap.recruitment_strategy.status).iconBg]">
            <component :is="nodeIcon(nodeMap.recruitment_strategy.status)" class="w-5 h-5" />
          </div>
          <div class="text-sm font-bold text-slate-700">招聘策略 Agent</div>
          <div class="text-[10px] font-bold mt-0.5" :class="nodeStyle(nodeMap.recruitment_strategy.status).textClass">
            {{ nodeMap.recruitment_strategy.status }}
          </div>
        </div>

        <!-- Connector -->
        <div class="w-8 h-[2px] bg-slate-200 relative flex-shrink-0">
          <div class="absolute right-0 top-1/2 -translate-y-1/2 w-0 h-0 border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent border-l-[6px] border-l-slate-300"></div>
        </div>

        <!-- Parallel Group 1 (Parser, Match) -->
        <div class="border border-dashed border-slate-300 rounded-3xl p-5 relative flex flex-col gap-4 bg-slate-50/50 flex-shrink-0">
          <span class="absolute -top-3 left-5 bg-slate-100 px-2.5 py-0.5 text-[9px] font-black tracking-widest text-slate-500 rounded-full uppercase border border-slate-200">
            Parallel Phase
          </span>
          
          <!-- Parser -->
          <div 
            @click="emit('select', 'resume_parser')"
            :class="[
              'w-56 rounded-2xl p-3.5 flex items-center gap-3.5 shadow-sm transition-all duration-300 cursor-pointer transform hover:translate-x-1',
              selectedNode === 'resume_parser' ? 'ring-2 ring-blue-500 ring-offset-2 scale-102' : '',
              nodeStyle(nodeMap.resume_parser.status).cardClass
            ]"
          >
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', nodeStyle(nodeMap.resume_parser.status).iconBg]">
              <component :is="nodeIcon(nodeMap.resume_parser.status)" class="w-5 h-5" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-bold text-slate-700 truncate">简历解析</div>
              <div class="text-[10px] font-bold mt-0.5" :class="nodeStyle(nodeMap.resume_parser.status).textClass">
                {{ nodeMap.resume_parser.status }}
              </div>
            </div>
          </div>
          
          <!-- Match -->
          <div 
            @click="emit('select', 'job_match')"
            :class="[
              'w-56 rounded-2xl p-3.5 flex items-center gap-3.5 shadow-sm transition-all duration-300 cursor-pointer transform hover:translate-x-1',
              selectedNode === 'job_match' ? 'ring-2 ring-blue-500 ring-offset-2 scale-102' : '',
              nodeStyle(nodeMap.job_match.status).cardClass
            ]"
          >
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', nodeStyle(nodeMap.job_match.status).iconBg]">
              <component :is="nodeIcon(nodeMap.job_match.status)" class="w-5 h-5" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-bold text-slate-700 truncate">岗位匹配</div>
              <div class="text-[10px] font-bold mt-0.5 animate-pulse" :class="nodeStyle(nodeMap.job_match.status).textClass">
                {{ nodeMap.job_match.status }}
              </div>
            </div>
          </div>
        </div>

        <!-- Connector -->
        <div class="w-8 h-[2px] bg-slate-200 relative flex-shrink-0">
          <div class="absolute right-0 top-1/2 -translate-y-1/2 w-0 h-0 border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent border-l-[6px] border-l-slate-300"></div>
        </div>

        <!-- Parallel Group 2 (Review, Report) -->
        <div class="border border-dashed border-slate-300 rounded-3xl p-5 relative flex flex-col gap-4 bg-slate-50/50 flex-shrink-0">
          <span class="absolute -top-3 left-5 bg-slate-100 px-2.5 py-0.5 text-[9px] font-black tracking-widest text-slate-500 rounded-full uppercase border border-slate-200">
            Decision & Reporting
          </span>
          
          <!-- Decision Review -->
          <div 
            @click="emit('select', 'decision_review')"
            :class="[
              'w-56 rounded-2xl p-3.5 flex items-center gap-3.5 shadow-sm transition-all duration-300 cursor-pointer transform hover:translate-x-1',
              selectedNode === 'decision_review' ? 'ring-2 ring-blue-500 ring-offset-2 scale-102' : '',
              nodeStyle(nodeMap.decision_review.status).cardClass
            ]"
          >
            <!-- Warning Ping Dot for NEEDS_REVIEW -->
            <template v-if="nodeMap.decision_review.status === AgentNodeStatus.NEEDS_REVIEW">
              <div class="absolute -top-1.5 -right-1.5 w-3.5 h-3.5 bg-amber-500 rounded-full animate-ping opacity-75"></div>
              <div class="absolute -top-1.5 -right-1.5 w-3.5 h-3.5 bg-amber-500 rounded-full border-2 border-white"></div>
            </template>
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', nodeStyle(nodeMap.decision_review.status).iconBg]">
              <component :is="nodeIcon(nodeMap.decision_review.status)" class="w-5 h-5" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-bold text-slate-700 truncate">决策审查</div>
              <div class="text-[10px] font-bold mt-0.5" :class="nodeStyle(nodeMap.decision_review.status).textClass">
                {{ nodeMap.decision_review.status }}
              </div>
            </div>
          </div>

          <!-- HR Report -->
          <div 
            @click="emit('select', 'hr_report')"
            :class="[
              'w-56 rounded-2xl p-3.5 flex items-center gap-3.5 shadow-sm transition-all duration-300 cursor-pointer transform hover:translate-x-1',
              selectedNode === 'hr_report' ? 'ring-2 ring-blue-500 ring-offset-2 scale-102' : '',
              nodeStyle(nodeMap.hr_report.status).cardClass
            ]"
          >
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', nodeStyle(nodeMap.hr_report.status).iconBg]">
              <component :is="nodeIcon(nodeMap.hr_report.status)" class="w-5 h-5" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-bold text-slate-700 truncate">HR 最终报告</div>
              <div class="text-[10px] font-bold mt-0.5" :class="nodeStyle(nodeMap.hr_report.status).textClass">
                {{ nodeMap.hr_report.status }}
              </div>
            </div>
          </div>
        </div>

        <!-- Connector -->
        <div class="w-8 h-[2px] bg-slate-200 relative flex-shrink-0">
          <div class="absolute right-0 top-1/2 -translate-y-1/2 w-0 h-0 border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent border-l-[6px] border-l-slate-300"></div>
        </div>

        <!-- Node 6: Interview Evaluation -->
        <div 
          @click="emit('select', 'interview_evaluation')"
          :class="[
            'w-40 h-28 rounded-2xl shadow-sm flex flex-col items-center justify-center relative transition-all duration-300 cursor-pointer transform hover:-translate-y-1',
            selectedNode === 'interview_evaluation' ? 'ring-2 ring-blue-500 ring-offset-2 scale-105' : '',
            nodeStyle(nodeMap.interview_evaluation.status).cardClass
          ]"
        >
          <div :class="['w-10 h-10 rounded-full flex items-center justify-center mb-2', nodeStyle(nodeMap.interview_evaluation.status).iconBg]">
            <component :is="nodeIcon(nodeMap.interview_evaluation.status)" class="w-5 h-5" />
          </div>
          <div class="text-sm font-bold text-slate-700">面试评估</div>
          <div class="text-[10px] font-bold mt-0.5" :class="nodeStyle(nodeMap.interview_evaluation.status).textClass">
            {{ nodeMap.interview_evaluation.status }}
          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, reactive, ref, type PropType } from 'vue';
import {
  AgentEventType,
  AgentNodeStatus,
  type AgentEvent,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';

// Lucide icon components mapped inline using SVG path components to avoid import weight
const CheckIcon = defineComponent({ render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.5' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M5 13l4 4L19 7' })]) });
const RefreshIcon = defineComponent({ render: () => h('svg', { class: 'animate-spin', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.5' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15' })]) });
const AlertIcon = defineComponent({ render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.5' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })]) });
const SlashIcon = defineComponent({ render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.5' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M18 12H6' })]) });
const DocIcon = defineComponent({ render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2.5' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' })]) });

const props = defineProps<{ snapshot: RecruitmentRunSnapshot | null; selectedNode?: string }>();
const emit = defineEmits<{ select: [nodeName: string] }>();

interface NodeView {
  name: string; label: string; status: AgentNodeStatus; action: string; duration: number | null;
  eventCount: number; skipReason: string; selected: boolean; tool: string; sourceCount: number; output: string;
}
const definitions = [
  ['recruitment_strategy', '招聘策略 Agent'], 
  ['resume_parser', '简历解析 Agent'], 
  ['job_match', '岗位匹配 Agent'],
  ['decision_review', '决策审查 Agent'], 
  ['hr_report', 'HR 最终报告'], 
  ['interview_evaluation', '面试评估 Agent'],
] as const;

const nodeMap = computed<Record<string, NodeView>>(() => Object.fromEntries(
  definitions.map(([name, label]) => [name, buildNode(name, label)]),
));

function buildNode(name: string, label: string): NodeView {
  const nodeEvents = (props.snapshot?.events || []).filter((event) => event.node_name === name);
  const actionEvent = findLast(nodeEvents, (event) => typeof event.summary.current_action === 'string');
  const toolEvent = findLast(nodeEvents, (event) => Boolean(event.tool_name));
  const durationEvent = findLast(nodeEvents, (event) => event.duration_ms !== null);
  const outputEvent = findLast(nodeEvents, (event) => [
    AgentEventType.INTERMEDIATE_RESULT, AgentEventType.AGENT_COMPLETED,
    AgentEventType.REVIEW_COMPLETED, AgentEventType.REPORT_GENERATED,
  ].includes(event.event_type));
  const status = props.snapshot?.nodes[name] || AgentNodeStatus.WAITING;
  const skipReason = status === AgentNodeStatus.SKIPPED ? resolveSkipReason(name, nodeEvents) : '';
  return {
    name, label, status,
    action: typeof actionEvent?.summary.current_action === 'string'
      ? actionEvent.summary.current_action : nodeEvents.at(-1)?.display_name || '等待运行',
    duration: durationEvent?.duration_ms ?? null,
    eventCount: nodeEvents.length,
    skipReason,
    selected: props.selectedNode === name,
    tool: toolEvent?.tool_name || '无',
    sourceCount: nodeEvents.reduce((max, event) => Math.max(max, event.source_count), 0),
    output: status === AgentNodeStatus.SKIPPED
      ? outputEvent ? summarize(outputEvent.summary) : skippedOutput(name)
      : summarize(outputEvent?.summary),
  };
}

function findLast(events: AgentEvent[], predicate: (event: AgentEvent) => boolean): AgentEvent | undefined {
  return [...events].reverse().find(predicate);
}

function summarize(summary: Record<string, unknown> | undefined): string {
  if (!summary) return '暂无结论';
  const preferred = summary.current_conclusion ?? summary.output_summary ?? summary.completed_node;
  if (typeof preferred === 'string') return preferred;
  const text = JSON.stringify(summary);
  return text.length > 100 ? `${text.slice(0, 97)}…` : text;
}

function resolveSkipReason(name: string, events: AgentEvent[]): string {
  const event = [...events].reverse().find((item) => item.status === AgentNodeStatus.SKIPPED);
  const directReason = event?.summary.skip_reason ?? event?.summary.reason;
  if (typeof directReason === 'string') return directReason;
  const reasons = event?.summary.skip_reasons;
  if (reasons && typeof reasons === 'object') {
    const nodeReason = (reasons as Record<string, unknown>)[name];
    if (typeof nodeReason === 'string') return nodeReason;
  }
  return name === 'interview_evaluation' ? 'STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE' : '跳过';
}

function skippedOutput(name: string): string {
  return name === 'interview_evaluation'
    ? '缺少结构化面试反馈。'
    : '跳过。';
}

// Map Node Status to styles
function nodeStyle(status: AgentNodeStatus) {
  switch (status) {
    case AgentNodeStatus.COMPLETED:
      return {
        cardClass: 'bg-white border border-slate-200 text-slate-800',
        iconBg: 'bg-emerald-50 text-emerald-500',
        textClass: 'text-emerald-500'
      };
    case AgentNodeStatus.RUNNING:
      return {
        cardClass: 'bg-white border-2 border-blue-400 relative overflow-hidden transform scale-[1.02] z-10',
        iconBg: 'bg-blue-100 text-blue-600',
        textClass: 'text-blue-600'
      };
    case AgentNodeStatus.NEEDS_REVIEW:
      return {
        cardClass: 'bg-white border border-amber-300',
        iconBg: 'bg-amber-50 text-amber-500',
        textClass: 'text-amber-500'
      };
    case AgentNodeStatus.SKIPPED:
      return {
        cardClass: 'bg-white/60 border border-slate-200/60 opacity-60',
        iconBg: 'bg-slate-100 text-slate-400',
        textClass: 'text-slate-400'
      };
    case AgentNodeStatus.FAILED:
      return {
        cardClass: 'bg-white border border-red-300',
        iconBg: 'bg-red-50 text-red-500',
        textClass: 'text-red-500'
      };
    case AgentNodeStatus.WAITING:
    default:
      return {
        cardClass: 'bg-slate-50 border border-slate-200 border-dashed',
        iconBg: 'bg-white text-slate-300 shadow-sm border border-slate-100',
        textClass: 'text-slate-300'
      };
  }
}

// Map Node Status to SVG Icon component
function nodeIcon(status: AgentNodeStatus) {
  switch (status) {
    case AgentNodeStatus.COMPLETED:
      return CheckIcon;
    case AgentNodeStatus.RUNNING:
      return RefreshIcon;
    case AgentNodeStatus.NEEDS_REVIEW:
    case AgentNodeStatus.FAILED:
      return AlertIcon;
    case AgentNodeStatus.SKIPPED:
      return SlashIcon;
    case AgentNodeStatus.WAITING:
    default:
      return DocIcon;
  }
}
</script>
