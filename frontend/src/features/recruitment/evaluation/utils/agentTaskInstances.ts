import {
  AgentEventType,
  AgentNodeStatus,
  type AgentEvent,
  type DecisionReviewSummary,
  type RecruitmentRunSnapshot,
} from '../../../../shared/agent/contracts';

export type AgentTaskInstanceStatus =
  | 'WAITING'
  | 'RUNNING'
  | 'COMPLETED'
  | 'NEEDS_REVIEW'
  | 'FAILED';

export interface AgentTaskInstance {
  candidateId: number | null;
  label: string;
  status: AgentTaskInstanceStatus;
  durationMs: number | null;
  startedAt: string | null;
  completedAt: string | null;
}

const CANDIDATE_COMPLETION_EVENTS = new Set<AgentEventType>([
  AgentEventType.TOOL_COMPLETED,
]);

const NODE_ACTIVITY_EVENTS = new Set<AgentEventType>([
  AgentEventType.AGENT_STARTED,
  AgentEventType.TOOL_STARTED,
  AgentEventType.TOOL_COMPLETED,
  AgentEventType.INTERMEDIATE_RESULT,
  AgentEventType.CANDIDATE_COMPLETED,
  AgentEventType.REVIEW_COMPLETED,
  AgentEventType.AGENT_COMPLETED,
]);

export function buildCandidateTaskInstances(
  snapshot: RecruitmentRunSnapshot,
  nodeName: string,
  candidateNames: Record<number, string>,
): AgentTaskInstance[] {
  const instances = new Map<number, AgentTaskInstance>(
    snapshot.candidate_ids.map((candidateId) => [candidateId, {
      candidateId,
      label: candidateNames[candidateId] || `候选人 #${candidateId}`,
      status: 'WAITING',
      durationMs: null,
      startedAt: null,
      completedAt: null,
    }]),
  );

  const candidateEvents = orderedEvents(snapshot.events).filter((event) =>
    event.node_name === nodeName
      && event.candidate_id !== null
      && instances.has(event.candidate_id),
  );

  for (const event of candidateEvents) {
    const instance = instances.get(event.candidate_id!);
    if (!instance) continue;

    if (event.error !== null || event.status === AgentNodeStatus.FAILED) {
      instance.status = 'FAILED';
      instance.completedAt = event.created_at;
      if (event.duration_ms !== null) instance.durationMs = event.duration_ms;
      continue;
    }

    if (event.status === AgentNodeStatus.NEEDS_REVIEW) {
      instance.status = 'NEEDS_REVIEW';
      instance.completedAt = event.created_at;
      if (event.duration_ms !== null) instance.durationMs = event.duration_ms;
      continue;
    }

    if (event.event_type === AgentEventType.TOOL_STARTED) {
      instance.status = 'RUNNING';
      instance.startedAt = event.created_at;
      instance.completedAt = null;
      continue;
    }

    const intermediateCompletes = event.event_type === AgentEventType.INTERMEDIATE_RESULT
      && (nodeName === 'resume_parser' || nodeName === 'job_match');
    const candidateCompletes = event.event_type === AgentEventType.CANDIDATE_COMPLETED
      && nodeName === 'resume_parser';
    const reviewCompletes = event.event_type === AgentEventType.REVIEW_COMPLETED
      && nodeName === 'decision_review';

    if (
      CANDIDATE_COMPLETION_EVENTS.has(event.event_type)
      || intermediateCompletes
      || candidateCompletes
      || reviewCompletes
    ) {
      instance.status = reviewCompletes && needsHumanReview(
        snapshot.decision_reviews[String(event.candidate_id)],
        event,
        snapshot.goal.confidence_threshold,
      ) ? 'NEEDS_REVIEW' : 'COMPLETED';
      instance.completedAt = event.created_at;
      if (event.duration_ms !== null && (
        event.event_type === AgentEventType.TOOL_COMPLETED
        || instance.durationMs === null
      )) {
        instance.durationMs = event.duration_ms;
      }
    }
  }

  applySnapshotFallbacks(snapshot, nodeName, instances, candidateEvents);
  enforceSingleRunningInstance(snapshot, nodeName, instances, candidateEvents);
  return snapshot.candidate_ids.map((candidateId) => instances.get(candidateId)!);
}

export function buildSingletonTaskInstance(
  snapshot: RecruitmentRunSnapshot,
  nodeName: 'recruitment_strategy' | 'hr_report',
  label: string,
): AgentTaskInstance {
  const nodeEvents = orderedEvents(snapshot.events).filter((event) => event.node_name === nodeName);
  const startedEvent = nodeEvents.find((event) => event.event_type === AgentEventType.AGENT_STARTED)
    ?? nodeEvents.find((event) => event.event_type === AgentEventType.TOOL_STARTED);
  const completedEvent = [...nodeEvents].reverse().find((event) =>
    event.event_type === AgentEventType.AGENT_COMPLETED
      || event.event_type === AgentEventType.TOOL_COMPLETED,
  );
  const failedEvent = [...nodeEvents].reverse().find((event) =>
    event.error !== null || event.status === AgentNodeStatus.FAILED,
  );
  const nodeStatus = snapshot.nodes[nodeName] ?? AgentNodeStatus.WAITING;

  let status = taskStatusFromNodeStatus(nodeStatus);
  if (status === 'WAITING' && completedEvent) status = taskStatusFromNodeStatus(completedEvent.status);
  if (status === 'WAITING' && startedEvent) status = 'RUNNING';
  if (nodeName === 'hr_report' && snapshot.report && status === 'WAITING') status = 'COMPLETED';
  if (failedEvent) status = 'FAILED';

  return {
    candidateId: null,
    label,
    status,
    durationMs: completedEvent?.duration_ms ?? failedEvent?.duration_ms ?? null,
    startedAt: startedEvent?.created_at ?? null,
    completedAt: status === 'COMPLETED' || status === 'NEEDS_REVIEW' || status === 'FAILED'
      ? completedEvent?.created_at ?? failedEvent?.created_at ?? null
      : null,
  };
}

export function hasNodeActivity(snapshot: RecruitmentRunSnapshot, nodeName: string): boolean {
  return snapshot.events.some((event) =>
    event.node_name === nodeName && NODE_ACTIVITY_EVENTS.has(event.event_type),
  );
}

function orderedEvents(events: AgentEvent[]): AgentEvent[] {
  return events
    .map((event, index) => ({ event, index }))
    .sort((left, right) => {
      const timeDifference = Date.parse(left.event.created_at) - Date.parse(right.event.created_at);
      return (Number.isNaN(timeDifference) ? 0 : timeDifference) || left.index - right.index;
    })
    .map(({ event }) => event);
}

function applySnapshotFallbacks(
  snapshot: RecruitmentRunSnapshot,
  nodeName: string,
  instances: Map<number, AgentTaskInstance>,
  candidateEvents: AgentEvent[],
): void {
  for (const [candidateId, instance] of instances) {
    const resultExists = nodeResultExists(snapshot, nodeName, candidateId);
    if (!resultExists || instance.status === 'FAILED' || instance.status === 'NEEDS_REVIEW') continue;

    if (nodeName === 'decision_review' && needsHumanReview(
      snapshot.decision_reviews[String(candidateId)],
      undefined,
      snapshot.goal.confidence_threshold,
    )) {
      instance.status = 'NEEDS_REVIEW';
      continue;
    }

    const hasCompletionEvent = candidateEvents.some((event) =>
      event.candidate_id === candidateId && (
        event.event_type === AgentEventType.TOOL_COMPLETED
        || event.event_type === AgentEventType.CANDIDATE_COMPLETED
        || event.event_type === AgentEventType.REVIEW_COMPLETED
      ),
    );
    if (!hasCompletionEvent && (instance.status === 'WAITING' || instance.status === 'RUNNING')) {
      instance.status = 'COMPLETED';
    }
  }
}

function enforceSingleRunningInstance(
  snapshot: RecruitmentRunSnapshot,
  nodeName: string,
  instances: Map<number, AgentTaskInstance>,
  candidateEvents: AgentEvent[],
): void {
  const currentCandidateId = snapshot.current_node === nodeName
    ? snapshot.current_candidate_id
    : null;
  const current = currentCandidateId === null ? undefined : instances.get(currentCandidateId);

  if (current && current.status !== 'COMPLETED' && current.status !== 'NEEDS_REVIEW' && current.status !== 'FAILED') {
    current.status = 'RUNNING';
  }

  let runningCandidateId = current?.status === 'RUNNING' ? currentCandidateId : null;
  if (runningCandidateId === null) {
    const latestTaskEvent = [...candidateEvents].reverse().find((event) =>
      event.event_type === AgentEventType.TOOL_STARTED
        || event.event_type === AgentEventType.TOOL_COMPLETED
        || event.event_type === AgentEventType.INTERMEDIATE_RESULT
        || event.event_type === AgentEventType.CANDIDATE_COMPLETED
        || event.event_type === AgentEventType.REVIEW_COMPLETED
        || event.error !== null,
    );
    runningCandidateId = latestTaskEvent?.event_type === AgentEventType.TOOL_STARTED
      && instances.get(latestTaskEvent.candidate_id!)?.status === 'RUNNING'
      ? latestTaskEvent.candidate_id
      : null;
  }

  for (const [candidateId, instance] of instances) {
    if (instance.status === 'RUNNING' && candidateId !== runningCandidateId) instance.status = 'WAITING';
  }
}

function nodeResultExists(
  snapshot: RecruitmentRunSnapshot,
  nodeName: string,
  candidateId: number,
): boolean {
  const key = String(candidateId);
  switch (nodeName) {
    case 'resume_parser':
      return Boolean(snapshot.candidate_profiles[key]);
    case 'job_match':
      return Boolean(snapshot.job_matches[key]);
    case 'interview_evaluation':
      return Boolean(snapshot.interview_evaluations[key]);
    case 'decision_review':
      return Boolean(snapshot.decision_reviews[key]);
    default:
      return false;
  }
}

function needsHumanReview(
  review?: DecisionReviewSummary,
  event?: AgentEvent,
  confidenceThreshold = 0,
): boolean {
  if (event?.status === AgentNodeStatus.NEEDS_REVIEW) return true;
  if (event && summarySignalsReview(event.summary)) return true;
  if (!review) return false;
  return review.confidence === null
    || review.confidence < confidenceThreshold
    || review.findings.some((finding) =>
      finding.requires_human_review || finding.severity.toUpperCase() === 'HIGH',
    );
}

function summarySignalsReview(summary: Record<string, unknown>): boolean {
  const reviewKeys = ['requires_review', 'review_required', 'needs_review', 'candidate_needs_review'];
  if (reviewKeys.some((key) => summary[key] === true)) return true;
  const nested = summary.decision_review;
  if (!nested || typeof nested !== 'object') return false;
  const candidate = nested as Partial<DecisionReviewSummary>;
  return Array.isArray(candidate.findings) && candidate.findings.some((finding) =>
    finding.requires_human_review || finding.severity?.toUpperCase() === 'HIGH',
  );
}

function taskStatusFromNodeStatus(status: AgentNodeStatus): AgentTaskInstanceStatus {
  switch (status) {
    case AgentNodeStatus.RUNNING:
      return 'RUNNING';
    case AgentNodeStatus.COMPLETED:
      return 'COMPLETED';
    case AgentNodeStatus.NEEDS_REVIEW:
      return 'NEEDS_REVIEW';
    case AgentNodeStatus.FAILED:
      return 'FAILED';
    default:
      return 'WAITING';
  }
}
