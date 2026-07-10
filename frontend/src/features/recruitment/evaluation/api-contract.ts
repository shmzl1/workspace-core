/** @deprecated 请直接使用 shared Agent 契约与 shared Agent API。 */

export type {
  AgentEvent,
  RecruitmentRunRequest,
  RecruitmentRunSnapshot,
} from '../../../shared/agent/contracts';

export type { AgentEventStreamCallbacks } from '../../../shared/api/modules/agent';

// Requests and SSE remain implemented only in shared/api/modules/agent.ts.
