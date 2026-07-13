/// <reference types="vite/client" />

import axios from 'axios';

export interface IntegrationHealthStatus {
  enabled: boolean;
  configured: boolean;
  ready: boolean;
  mode: string;
}

export interface LlmHealthStatus extends IntegrationHealthStatus {
  provider: string;
  model_name: string | null;
}

export interface RagHealthStatus extends IntegrationHealthStatus {
  collection_name: string | null;
  document_count: number | null;
  chunk_count: number | null;
}

export interface BackendHealth {
  status: string;
  overall_mode: string;
  integrations: {
    llm: LlmHealthStatus;
    rag: RagHealthStatus;
  };
  run_store: {
    mode: string;
  };
}

interface HealthEnvelope {
  success: boolean;
  data: BackendHealth;
}

const configuredBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim();
const healthUrl = configuredBaseUrl
  ? `${configuredBaseUrl.replace(/\/api\/v1\/?$/, '')}/health`
  : '/health';

export async function checkBackendHealth(): Promise<void> {
  await getBackendHealth();
}

export async function getBackendHealth(): Promise<BackendHealth> {
  const response = await axios.get<HealthEnvelope>(healthUrl, { timeout: 5_000 });
  return response.data.data;
}
