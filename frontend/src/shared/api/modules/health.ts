import axios from 'axios';

const configuredBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim();
const healthUrl = configuredBaseUrl
  ? `${configuredBaseUrl.replace(/\/api\/v1\/?$/, '')}/health`
  : '/health';

export async function checkBackendHealth(): Promise<void> {
  await axios.get(healthUrl, { timeout: 5_000 });
}
