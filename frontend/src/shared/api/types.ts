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

export type AlgorithmStatus =
  | 'algorithm_not_ready'
  | 'candidate_availability_missing'
  | 'interviewer_availability_missing'
  | 'room_availability_missing'
  | 'no_available_slot'
  | 'scored'
  | 'schedule_generated'
  | 'success'
  | 'reviewed'
  | string;

export interface AlgorithmAwareResponse {
  status: AlgorithmStatus;
  message: string;
  expected_module?: string | null;
  expected_function?: string | null;
  fallback_data?: Record<string, unknown>;
  requires_human_only?: boolean;
}

// ── 枚举字面量 ─────────────────────────────

export type EmploymentType = 'INTERN' | 'FULL_TIME' | 'PART_TIME';
export type JobStatus = 'DRAFT' | 'OPEN' | 'CLOSED';
export type CandidateSource = 'MANUAL' | 'UPLOAD' | 'SEED' | 'REFERRAL';

export type CandidateResumeImportStatus = 'IMPORTED' | 'DUPLICATE' | 'FAILED';

export interface CandidateResumeImportItem {
  filename: string;
  status: CandidateResumeImportStatus;
  full_name: string | null;
  matched_job_id: number | null;
  matched_job_title: string | null;
  candidate_id: number | null;
  application_id: number | null;
  message: string;
}

export interface CandidateResumeImportResponse {
  imported_count: number;
  duplicate_count: number;
  failed_count: number;
  items: CandidateResumeImportItem[];
}

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
  score_breakdown: Record<string, unknown>;
  weights_snapshot: Record<string, unknown>;
  scored_at: string | null;
  applied_at: string;
  updated_at: string;
}

export interface CandidateScoreRequest {
  weights: Record<string, number>;
  note?: string;
}

export interface CandidateScoreResponse extends AlgorithmAwareResponse {
  application_id: number;
  score_total?: number | null;
  overall_score?: number | null;
  match_score?: number | null;
  match_rate?: number | null;
  skill_match?: string | null;
  experience_match?: string | null;
  education_match?: string | null;
  risk_tags?: string[];
  risk_prompt?: string | null;
  recommended_action?: string | null;
  scoring_basis?: string[];
  reasons?: string[];
  score_breakdown?: Record<string, unknown>;
  explanation?: Record<string, unknown>;
}

export interface RecruitmentFunnelItem { label: string; count: number; rate: number; }
export interface RecruitmentDepartmentItem {
  department: string; jobs_count: number; applications_count: number; hired_count: number; completion_rate: number;
}
export interface RecruitmentSourceItem { source: string; count: number; rate: number; }
export interface RecruitmentTrendItem {
  period: string; applications_count: number; hired_count: number; average_score: number;
}
export interface RecruitmentReportResponse {
  time_range: '30d' | '90d' | 'all';
  jobs_count: number;
  open_jobs_count: number;
  candidates_count: number;
  applications_count: number;
  scored_applications_count: number;
  pending_score_count: number;
  high_match_count: number;
  interview_pending_count: number;
  interviewing_count: number;
  offered_count: number;
  hired_count: number;
  rejected_count: number;
  average_score: number;
  average_match_rate: number;
  funnel: RecruitmentFunnelItem[];
  departments: RecruitmentDepartmentItem[];
  sources: RecruitmentSourceItem[];
  trends: RecruitmentTrendItem[];
}

export interface SchedulePreviewRequest {
  application_id: number;
  duration_minutes?: number;
  interviewer_ids?: number[];
}

export interface SchedulePreviewResponse extends AlgorithmAwareResponse {
  recommended_time?: Record<string, unknown> | null;
  recommended_interviewer_id?: number | null;
  recommended_interviewer?: string | null;
  recommended_room_id?: number | null;
  recommended_room?: string | null;
  interviewer_availability?: string | null;
  candidate_availability?: string | null;
  conflict_detection?: string | null;
  recommendation_reason?: string | null;
  conflict_explanation?: Record<string, unknown>;
}

export interface PayrollPreAuditRequest {
  requester_role: string;
  requester_employee_id?: number | null;
  target_record_ids?: number[];
  include_line_items?: boolean;
}

export interface PayrollPreAuditResponse extends AlgorithmAwareResponse {
  pending_batches: number;
  abnormal_salary_items: Array<Record<string, unknown>>;
  permission_risks: Array<Record<string, unknown>>;
  deduction_sources: Array<Record<string, unknown>>;
  approval_suggestion?: string | null;
  risk_level?: string | null;
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

export interface CandidateApplicationDetail {
  application: CandidateApplication & { candidate_name?: string | null; job_title?: string | null };
  candidate: Candidate;
  job: Job;
  pipeline_records: CandidatePipelineRecord[];
}

export interface AdvanceStageResponse {
  application: CandidateApplication & { candidate_name?: string | null; job_title?: string | null };
  pipeline_record: CandidatePipelineRecord;
}

export interface InterviewRecord {
  id: number;
  application_id: number;
  interviewer_id: number;
  meeting_room_id: number;
  start_at: string;
  end_at: string;
  status: string;
  conflict_explanation: Record<string, unknown>;
  created_by_user_id: number | null;
}

export interface ConfirmInterviewScheduleRequest {
  application_id: number;
  interviewer_id: number;
  meeting_room_id: number;
  start_at: string;
  end_at: string;
  conflict_explanation?: Record<string, unknown>;
}

export interface AvailabilitySlotWrite {
  start_at: string;
  end_at: string;
}

export interface InterviewAvailabilityBatchWrite {
  candidates: Array<{
    candidate_id: number;
    duration_minutes: number;
    slots: AvailabilitySlotWrite[];
  }>;
  interviewers: Array<{
    interviewer_id: number;
    slots: AvailabilitySlotWrite[];
  }>;
}

export interface InterviewAvailabilityBatchResult {
  candidate_count: number;
  interviewer_count: number;
  slot_count: number;
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
