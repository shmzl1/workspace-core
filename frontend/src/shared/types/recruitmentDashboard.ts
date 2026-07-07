export interface SidebarGroup {
  title: string;
  items: string[];
}

export interface KpiItem {
  id: string;
  label: string;
  value: string;
  trend?: string;
  variant: 'plain' | 'gradient' | 'bars' | 'dark';
}

export interface PipelineStage {
  title: string;
  candidate: string;
  status: string;
  progress?: number;
  match?: string;
  tags?: string[];
}

export interface ScheduleItem {
  day: string;
  date: string;
  name: string;
  role: string;
  time: string;
}
