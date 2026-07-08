/**
 * API 层通用类型定义
 *
 * 所有接口类型与后端 ORM 模型一一对应，
 * 确保前后端字段命名一致（snake_case → 前端原样传递，由后端序列化）。
 */

// ── 统一响应结构 ───────────────────────────

export interface ApiError {
  code: string;
  message: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: ApiError | null;
  trace_id: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ── 枚举字面量 ─────────────────────────────

export type EmploymentType = 'INTERN' | 'FULL_TIME' | 'PART_TIME';
export type JobStatus = 'DRAFT' | 'OPEN' | 'CLOSED';
export type CandidateSource = 'MANUAL' | 'UPLOAD' | 'SEED' | 'REFERRAL';

export type PipelineStage =
  | 'APPLIED'
  | 'AI_SCREENED'
  | 'INTERVIEW_PENDING'
  | 'INTERVIEWING'
  | 'DECISION_PENDING'
  | 'OFFERED'
  | 'HIRED'
  | 'REJECTED';

export type EmploymentStatus = 'ACTIVE' | 'INACTIVE' | 'ON_LEAVE';

export type AttendanceStatus =
  | 'NORMAL'
  | 'LATE'
  | 'EARLY_LEAVE'
  | 'ABSENT'
  | 'UNPAID_LEAVE'
  | 'APPROVED_ANNUAL_LEAVE';

export type AttendanceSource = 'WEB' | 'MINIPROGRAM' | 'MANUAL' | 'SEED';

export type LeaveType = 'ANNUAL';

// ── Recruitment ──────────────────────────────

export interface Job {
  id: number;
  job_code: string;
  title: string;
  department: string;
  description: string | null;
  required_skills: string[];
  preferred_skills: string[];
  min_experience_months: number;
  location: string | null;
  employment_type: EmploymentType;
  status: JobStatus;
  owner_user_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface Candidate {
  id: number;
  candidate_no: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  resume_file_path: string | null;
  resume_text: string | null;
  skills: string[];
  experience_months: number;
  available_from: string | null; // date
  source: CandidateSource;
  profile_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CandidateApplication {
  id: number;
  candidate_id: number;
  job_id: number;
  current_stage: PipelineStage;
  score_total: number | null;
  score_breakdown: Record<string, number>;
  weights_snapshot: Record<string, number>;
  scored_at: string | null;
  applied_at: string;
  updated_at: string;
}

export interface CandidatePipelineRecord {
  id: number;
  application_id: number;
  from_stage: PipelineStage | null;
  to_stage: PipelineStage;
  note: string | null;
  changed_by_user_id: number | null;
  created_at: string;
}

// ── Employee ────────────────────────────────

export interface Employee {
  id: number;
  user_id: number | null;
  employee_no: string;
  full_name: string;
  department: string;
  job_title: string;
  manager_employee_id: number | null;
  email: string | null;
  phone: string | null;
  hire_date: string | null;
  employment_status: EmploymentStatus;
  created_at: string;
  updated_at: string;
}

export interface LeaveBalance {
  id: number;
  employee_id: number;
  leave_type: LeaveType;
  year: number;
  total_days: number;
  used_days: number;
  created_at: string;
  updated_at: string;
}

// ── Attendance ──────────────────────────────

export interface WorkCalendar {
  id: number;
  calendar_date: string;
  is_workday: boolean;
  standard_check_in_time: string; // time
  standard_check_out_time: string; // time
  late_grace_minutes: number;
  holiday_name: string | null;
  remark: string | null;
  created_at: string;
  updated_at: string;
}

export interface AttendanceRecord {
  id: number;
  employee_id: number;
  attendance_date: string;
  check_in_at: string | null;
  check_out_at: string | null;
  status: AttendanceStatus;
  late_minutes: number;
  early_leave_minutes: number;
  leave_balance_id: number | null;
  source: AttendanceSource;
  remark: string | null;
  created_at: string;
  updated_at: string;
}

// ── Aggregated / composite types ────────────

/** 候选人列表项（含关联岗位与阶段摘要） */
export interface CandidateSummary {
  candidate: Candidate;
  job_title: string;
  current_stage: PipelineStage;
  score_total: number | null;
}

/** 仪表盘 KPI 摘要 */
export interface DashboardKpi {
  open_positions: number;
  total_candidates: number;
  interviewing_count: number;
  offer_acceptance_rate: number;
  avg_time_to_hire_days: number;
}

/** Agent Trace 行 */
export interface AgentTrace {
  id: string;
  task: string;
  status: 'pending' | 'running' | 'done' | 'failed';
  summary: string;
  created_at: string;
}
