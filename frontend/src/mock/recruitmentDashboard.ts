import type { KpiItem, PipelineStage, ScheduleItem, SidebarGroup } from '../shared/types/recruitmentDashboard';

export const topNavItems = ['招聘看板', '候选人', '面试排期', '政策中心'];

export const sidebarGroups: SidebarGroup[] = [
  {
    title: '工作台',
    items: ['智能招聘看板', '候选人池', '面试日历', '招聘报告']
  },
  {
    title: 'AI Agent',
    items: ['智能筛选', '面试助手', '制度问答']
  },
  {
    title: '管理',
    items: ['权限审计', '系统设置']
  }
];

export const kpiItems: KpiItem[] = [
  { id: 'resumes', label: '新增简历', value: '12', trend: '+14%', variant: 'plain' },
  { id: 'screened', label: 'AI 筛选完成', value: '5', trend: '活跃中', variant: 'gradient' },
  { id: 'interviews', label: '进入面试阶段', value: '3', variant: 'bars' },
  { id: 'graph', label: 'LangGraph 链路动态', value: '实时', variant: 'dark' }
];

export const pipelineStages: PipelineStage[] = [
  {
    title: '原始提取',
    candidate: 'Alex Lee',
    status: '正在解析 PDF...'
  },
  {
    title: '语义匹配',
    candidate: 'Michael Chen',
    status: '技能匹配中',
    progress: 64
  },
  {
    title: '顶级匹配',
    candidate: 'Sarah Jenkins',
    status: '候选人画像已生成',
    match: '98% 匹配',
    tags: ['React', '领导力', '系统设计']
  }
];

export const weeklySchedule: ScheduleItem[] = [
  {
    day: '周一',
    date: '14',
    name: 'Sarah Jenkins',
    role: '高级前端工程师',
    time: '10:00 AM'
  },
  {
    day: '周二',
    date: '15',
    name: 'Michael Chen',
    role: '产品经理',
    time: '2:30 PM'
  },
  {
    day: '周四',
    date: '17',
    name: 'Elena Rodriguez',
    role: 'UX 设计师',
    time: '11:15 AM'
  }
];

export const heatmapRows = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

export const quickCommands = [
  '筛选 Java 后端候选人',
  '安排本周技术面',
  '生成招聘周报'
];

export const initialTraceLogs = [
  '正在查询候选人 “React.js” 相关技能知识图谱...',
  '候选人评分 Tool 已完成模拟计算',
  'RAG 来源追踪等待后端 Agent 接入'
];

export function buildHeatmapValues(): number[] {
  return Array.from({ length: 7 * 18 }, (_, index) => {
    const row = Math.floor(index / 18);
    const col = index % 18;
    return ((row * 3 + col * 2 + (col > 9 ? 2 : 0)) % 5) + 1;
  });
}
