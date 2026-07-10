/** Feature-local compatibility exports for the canonical Agent API contracts. */

export type {
  AgentEvent,
  RecruitmentRunRequest,
  RecruitmentRunSnapshot,
} from '../../../shared/agent/contracts';

export type { AgentEventStreamCallbacks } from '../../../shared/api/modules/agent';

// Requests and SSE remain implemented only in shared/api/modules/agent.ts.
