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

export interface KnowledgeSourceReference {
  source_id: string;
  title: string;
  document_type: string | null;
  department: string | null;
  job_code: string | null;
  version: string | null;
  effective_from: string | null;
  effective_to: string | null;
  effective_date: string | null;
  excerpt: string | null;
  relevance: number | null;
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
  sources: KnowledgeSourceReference[];
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

export interface ResumeEvidenceItem {
  evidence_id: string;
  capability: string;
  excerpt: string;
  source_section: string | null;
  supports: boolean | null;
  confidence: number | null;
}

export interface CandidateProfile {
  candidate_id: number;
  skills: string[];
  normalized_skills: string[];
  experience_months: number | null;
  education: string[];
  projects: string[];
  project_roles: string[];
  project_technologies: string[];
  measurable_achievements: string[];
  certificates: string[];
  availability: string | null;
  missing_fields: string[];
  evidence_items: ResumeEvidenceItem[];
}

export interface JobRequirementItem {
  requirement_id: string;
  category: string;
  description: string;
  required: boolean;
  weight: number | null;
  source_ids: string[];
}

export interface JobRubric {
  job_id: number;
  version: string | null;
  requirements: JobRequirementItem[];
}

export interface JobMatchSummary {
  candidate_id: number;
  overall_score: number | null;
  job_match_score: number | null;
  dimension_scores: Record<string, number>;
  must_have_passed: boolean | null;
  matched_skills: string[];
  missing_skills: string[];
  evidence_ids: string[];
  knowledge_sources: KnowledgeSourceReference[];
  suggested_interview_questions: string[];
  recommended_action: string | null;
}

export interface InterviewEvaluationInput {
  candidate_id: number;
  interview_id: number | null;
  interview_status: string;
  interviewer_scores: Record<string, number>;
  structured_feedback: Record<string, unknown>;
}

export interface InterviewEvaluationSummary {
  candidate_id: number;
  interview_id: number | null;
  status: string;
  conclusion: string;
  strengths: string[];
  risks: string[];
  evidence: string[];
  conflicts: string[];
  requires_review: boolean;
}

export interface DecisionReviewFinding {
  code: string;
  severity: string;
  summary: string;
  evidence_ids: string[];
  requires_human_review: boolean;
}

export interface DecisionReviewSummary {
  candidate_id: number;
  confidence: number | null;
  findings: DecisionReviewFinding[];
  risk_tags: string[];
  agent_disagreements: string[];
  deterministic_score_preserved: boolean;
  recommended_action: string | null;
}

export interface HRReportSummary {
  goal: RecruitmentGoal;
  candidate_rankings: number[];
  candidate_reviews: DecisionReviewSummary[];
  knowledge_sources: KnowledgeSourceReference[];
  talent_gaps: string[];
  next_actions: string[];
  requires_human_decision: boolean;
}

