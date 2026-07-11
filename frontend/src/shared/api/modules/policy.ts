import apiClient from '../apiClient';

export interface PolicyDocument {
  id: number;
  document_code: string;
  title: string;
  category: string;
  source_path: string | null;
  version: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface PolicyOverview {
  documents: PolicyDocument[];
  categories: Array<{ category: string; count: number }>;
}

export async function fetchPolicies(query?: string): Promise<PolicyOverview> {
  const response = await apiClient.get<PolicyOverview>('/policies', { params: { query } });
  return response.data;
}
