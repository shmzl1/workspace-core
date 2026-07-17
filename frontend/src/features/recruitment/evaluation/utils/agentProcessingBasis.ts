import {
  AgentNodeStatus,
  type AgentEvent,
  type KnowledgeSourceReference,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';

export const agentNodeNames = [
  'recruitment_strategy',
  'resume_parser',
  'job_match',
  'decision_review',
  'hr_report',
  'interview_evaluation',
] as const;

export type AgentNodeName = (typeof agentNodeNames)[number];

export interface AgentMetadata {
  title: string;
  responsibility: string;
  expectedInputs: string[];
}

export const agentMetadata: Record<AgentNodeName, AgentMetadata> = {
  recruitment_strategy: {
    title: '招聘策略 Agent',
    responsibility: '读取招聘目标、岗位要求和候选人范围，制定本次多 Agent 执行计划，并检索企业岗位知识。',
    expectedInputs: ['招聘目标与岗位要求', '候选人范围', '企业招聘标准', '岗位评分规则'],
  },
  resume_parser: {
    title: '简历解析 Agent',
    responsibility: '从安全白名单字段和已脱敏简历片段中提取技能、经历、项目、成果、缺失项以及可定位证据。',
    expectedInputs: ['候选人编号', '已脱敏简历结构化字段', '证据所在简历章节'],
  },
  job_match: {
    title: '岗位匹配 Agent',
    responsibility: '结合岗位评分标准、候选人画像和企业知识，对候选人的岗位匹配程度进行确定性评估。',
    expectedInputs: ['招聘目标', '岗位评分规则', '结构化候选人画像', '企业岗位知识'],
  },
  decision_review: {
    title: '决策审查 Agent',
    responsibility: '检查评分阈值、必备条件、证据完整性、风险项、面试数据和 Agent 结果一致性。',
    expectedInputs: ['可信度阈值', '候选人画像', '岗位匹配结果', '真实面试评估（如有）'],
  },
  hr_report: {
    title: 'HR 最终报告',
    responsibility: '汇总候选人排序、匹配结果、风险、人才缺口、知识来源和后续动作，生成供 HR 决策的结构化报告。',
    expectedInputs: ['招聘目标', '岗位匹配结果', '决策审查结果', '企业知识来源'],
  },
  interview_evaluation: {
    title: '面试评估 Agent',
    responsibility: '基于真实的结构化面试评分和面试官反馈生成面试结论；缺少真实数据时必须跳过。',
    expectedInputs: ['真实结构化面试评分', '面试官结构化反馈', '面试证据'],
  },
};

export const toolLabels: Record<string, string> = {
  retrieve_enterprise_knowledge: '检索企业岗位知识',
  extract_candidate_profile: '提取候选人结构化画像',
  evaluate_candidate: '执行岗位匹配评估',
  review_candidate_decision: '执行招聘决策审查',
  build_recruitment_report: '生成 HR 招聘报告',
};

const preferredSummaryKeys = [
  'current_action',
  'current_goal',
  'next_action',
  'completed_node',
  'candidate_count',
  'evaluated_candidates',
  'reviewed_candidates',
  'profile_count',
  'evidence_count',
  'overall_score',
  'job_match_score',
  'confidence',
  'finding_count',
  'review_required',
  'requires_review',
  'generation_mode',
  'retrieval_mode',
  'scoring_mode',
  'skip_reason',
] as const;

const sensitiveKeyPattern = /password|secret|authorization|api_key|phone|email|id_card|salary_budget|system_prompt|chain_of_thought|reasoning|(^|_)prompt($|_)/i;
const allowedTokenStatistics = new Set(['prompt_tokens', 'completion_tokens', 'total_tokens']);

export interface FormattedEventSummary {
  preferred: Array<{ key: string; label: string; value: unknown }>;
  extra: Record<string, unknown>;
}

export const summaryLabels: Record<string, string> = {
  current_action: '当前动作',
  current_goal: '当前目标',
  next_action: '下一步动作',
  completed_node: '完成节点',
  candidate_count: '候选人数',
  evaluated_candidates: '已评估候选人',
  reviewed_candidates: '已审查候选人',
  profile_count: '画像数量',
  evidence_count: '证据数量',
  overall_score: '综合得分',
  job_match_score: '岗位匹配得分',
  confidence: '可信度',
  finding_count: '发现项数量',
  review_required: '需要复核',
  requires_review: '需要复核',
  generation_mode: '生成模式',
  retrieval_mode: '检索模式',
  scoring_mode: '评分模式',
  skip_reason: '跳过原因',
};

export function isAgentNodeName(value: string | null): value is AgentNodeName {
  return value !== null && (agentNodeNames as readonly string[]).includes(value);
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export function nodeEventsFor(
  snapshot: RecruitmentRunSnapshot | null,
  nodeName: string | null,
): AgentEvent[] {
  if (!snapshot || !nodeName) return [];
  return snapshot.events
    .filter((event) => event.node_name === nodeName)
    .sort((left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime());
}

export function nodeStatusFor(
  snapshot: RecruitmentRunSnapshot | null,
  nodeName: string | null,
): AgentNodeStatus {
  if (!snapshot || !nodeName) return AgentNodeStatus.WAITING;
  return snapshot.nodes[nodeName] ?? AgentNodeStatus.WAITING;
}

export function candidateLabel(candidateId: number, candidateNames: Record<number, string>): string {
  return candidateNames[candidateId] || `候选人 #${candidateId}`;
}

export function toolLabel(toolName: string): string {
  return toolLabels[toolName] ?? toolName;
}

export function uniqueToolNames(events: AgentEvent[]): string[] {
  return [...new Set(events.flatMap((event) => event.tool_name ? [event.tool_name] : []))];
}

export function latestStringSummary(events: AgentEvent[], key: string): string | null {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const value = events[index]?.summary[key];
    if (typeof value === 'string' && value.trim()) return value;
  }
  return null;
}

export function resolveSkipReason(nodeName: string | null, events: AgentEvent[]): string | null {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const event = events[index];
    if (!event) continue;
    const directReason = event.summary.skip_reason ?? event.summary.reason;
    if (typeof directReason === 'string' && directReason) return directReason;
    const reasons = event.summary.skip_reasons;
    if (nodeName && isRecord(reasons) && typeof reasons[nodeName] === 'string') {
      return reasons[nodeName];
    }
  }
  return nodeName === 'interview_evaluation'
    ? 'STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE'
    : null;
}

export function formatEventSummary(summary: Record<string, unknown>): FormattedEventSummary {
  const sanitized = sanitizeRecord(summary);
  const preferred = preferredSummaryKeys.flatMap((key) => {
    if (!(key in sanitized)) return [];
    return [{ key, label: summaryLabels[key] ?? key, value: sanitized[key] }];
  });
  const preferredKeySet = new Set(preferredSummaryKeys);
  const extra = Object.fromEntries(
    Object.entries(sanitized).filter(([key]) => !preferredKeySet.has(key as (typeof preferredSummaryKeys)[number])),
  );
  return { preferred, extra };
}

export function sanitizeStructuredValue(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sanitizeStructuredValue).filter((item) => item !== undefined);
  }
  if (isRecord(value)) return sanitizeRecord(value);
  if (['string', 'number', 'boolean'].includes(typeof value) || value === null) return value;
  return undefined;
}

export function isEmptyRecord(value: Record<string, unknown>): boolean {
  return Object.keys(value).length === 0;
}

export function mergeKnowledgeSources(
  snapshot: RecruitmentRunSnapshot | null,
  selectedCandidateId: number | null,
): KnowledgeSourceReference[] {
  if (!snapshot) return [];
  const candidateSources = selectedCandidateId === null
    ? []
    : snapshot.job_matches[String(selectedCandidateId)]?.knowledge_sources ?? [];
  const sources = [
    ...snapshot.sources,
    ...(snapshot.knowledge_summary?.sources ?? []),
    ...candidateSources,
    ...(snapshot.report?.knowledge_sources ?? []),
  ];
  return [...new Map(sources.map((source) => [source.source_id, source])).values()];
}

function sanitizeRecord(value: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(value).flatMap(([key, item]) => {
      if (isSensitiveKey(key)) return [];
      const sanitized = sanitizeStructuredValue(item);
      return sanitized === undefined ? [] : [[key, sanitized]];
    }),
  );
}

function isSensitiveKey(key: string): boolean {
  if (allowedTokenStatistics.has(key.toLowerCase())) return false;
  return sensitiveKeyPattern.test(key);
}
