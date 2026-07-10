/** Canonical frontend contracts aligned with backend Agent Pydantic models. */

export enum AgentRunStatus {
  PENDING = 'PENDING',
  RUNNING = 'RUNNING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
}

export enum AgentNodeStatus {
  WAITING = 'WAITING',
  RUNNING = 'RUNNING',
  COMPLETED = 'COMPLETED',
  NEEDS_REVIEW = 'NEEDS_REVIEW',
  FAILED = 'FAILED',
  SKIPPED = 'SKIPPED',
}

export enum AgentEventType {
  WORKFLOW_STARTED = 'WORKFLOW_STARTED',
  PLAN_CREATED = 'PLAN_CREATED',
  AGENT_STARTED = 'AGENT_STARTED',
  AGENT_THINKING = 'AGENT_THINKING',
  TOOL_STARTED = 'TOOL_STARTED',
  TOOL_COMPLETED = 'TOOL_COMPLETED',
  KNOWLEDGE_RETRIEVED = 'KNOWLEDGE_RETRIEVED',
  INTERMEDIATE_RESULT = 'INTERMEDIATE_RESULT',
  AGENT_COMPLETED = 'AGENT_COMPLETED',
  CANDIDATE_COMPLETED = 'CANDIDATE_COMPLETED',
  REVIEW_COMPLETED = 'REVIEW_COMPLETED',
  REPORT_GENERATED = 'REPORT_GENERATED',
  WORKFLOW_COMPLETED = 'WORKFLOW_COMPLETED',
  WORKFLOW_FAILED = 'WORKFLOW_FAILED',
}

export interface AgentErrorInfo {
  code: string;
  message: string;
  retriable: boolean;
  details: Record<string, unknown>;
}

export interface AgentEvent {
  event_id: string;
  run_id: string;
  trace_id: string;
  candidate_id: number | null;
  agent_name: string | null;
  node_name: string | null;
  display_name: string;
  event_type: AgentEventType;
  status: AgentNodeStatus;
  /** Auditable structured stage summary, never hidden chain-of-thought. */
  summary: Record<string, unknown>;
  tool_name: string | null;
  source_count: number;
  duration_ms: number | null;
  fallback_used: boolean;
  created_at: string;
  error: AgentErrorInfo | null;
}

export interface AgentRunSnapshot {
  run_id: string;
  trace_id: string;
  status: AgentRunStatus;
  current_agent: string | null;
  current_node: string | null;
  completed_candidates: number;
  total_candidates: number;
  nodes: Record<string, AgentNodeStatus>;
  events: AgentEvent[];
  error: AgentErrorInfo | null;
  created_at: string;
  updated_at: string;
}

export type RecruitmentUrgency = 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL';

export interface RecruitmentGoal {
  job_id: number;
  job_title: string;
  department: string;
  target_headcount: number;
  deadline: string | null;
  required_skills: string[];
  preferred_skills: string[];
  min_experience_months: number;
  score_threshold: number;
  confidence_threshold: number;
  urgency: RecruitmentUrgency;
  optional_salary_budget: number | null;
}

export interface RecruitmentRunRequest {
  goal: RecruitmentGoal;
  candidate_ids: number[];
}

export interface RecruitmentExecutionPlan {
  goal: RecruitmentGoal;
  candidate_ids: number[];
  candidate_count: number;
  required_nodes: string[];
  executed_nodes: string[];
  skipped_nodes: string[];
  interview_evaluation_requires_real_data: boolean;
  current_phase: 'SPRINT_2_1_STRATEGY_ONLY';
  next_phase: 'SPRINT_2_2';
  plan_notes: string[];
}

export interface RecruitmentRunSnapshot extends AgentRunSnapshot {
  execution_plan: RecruitmentExecutionPlan | null;
}

