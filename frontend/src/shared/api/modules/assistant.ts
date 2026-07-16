import apiClient from '../apiClient';

export type AssistantIntent = 'LEAVE' | 'PAYROLL' | 'POLICY' | 'CHAT' | 'UNKNOWN';

export interface AssistantChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AssistantResolvedParameters {
  year?: number | null;
  month?: number | null;
  policy_keywords: string[];
}

export interface AssistantChatRequest {
  message: string;
  conversation_summary: string;
  recent_messages: AssistantChatMessage[];
}

export interface AssistantChatResponse {
  intent: AssistantIntent;
  normalized_query: string;
  reply: string;
  parameters: AssistantResolvedParameters;
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
