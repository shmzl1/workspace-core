import apiClient from '../apiClient';

export type AssistantIntent = 'LEAVE' | 'PAYROLL' | 'POLICY' | 'CHAT' | 'UNKNOWN';
export type AssistantResponseMode = 'QUERY_DATA' | 'ANSWER_FROM_RESULT' | 'CHAT' | 'UNKNOWN';
export type AssistantResultOperation = 'NONE' | 'READ' | 'CONFIRM' | 'COMPARE' | 'EXPLAIN';

export interface AssistantChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AssistantResolvedParameters {
  year?: number | null;
  month?: number | null;
  policy_keywords: string[];
}

export interface AssistantAvailableFact {
  key: string;
  label: string;
  unit?: string | null;
  value_type: 'number' | 'text' | 'boolean' | 'date';
}

export interface AssistantAvailableResultContext {
  domain: 'LEAVE' | 'PAYROLL' | 'POLICY';
  query_summary: string;
  primary_fact_key?: string | null;
  available_facts: AssistantAvailableFact[];
}

export interface AssistantResultReference {
  operation: AssistantResultOperation;
  fact_keys: string[];
  candidate_number?: number | null;
  candidate_text?: string | null;
}

export interface AssistantChatRequest {
  message: string;
  conversation_summary: string;
  recent_messages: AssistantChatMessage[];
  available_result_context?: AssistantAvailableResultContext | null;
}

export interface AssistantChatResponse {
  response_mode: AssistantResponseMode;
  intent: AssistantIntent;
  normalized_query: string;
  reply: string;
  parameters: AssistantResolvedParameters;
  result_reference: AssistantResultReference;
  updated_summary: string;
  context: {
    recent_message_count: number;
    summary_used: boolean;
  };
}

export async function sendAssistantChat(
  payload: AssistantChatRequest,
): Promise<AssistantChatResponse> {
  const response = await apiClient.post<AssistantChatResponse>('/assistant/chat', payload);
  return response.data;
}
