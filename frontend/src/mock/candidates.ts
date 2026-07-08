/**
 * 候选人样例数据
 */
import type { CandidateSummary } from '../shared/api/types';

export const mockCandidates: CandidateSummary[] = [
  {
    candidate: {
      id: 1,
      candidate_no: 'C-2026-001',
      full_name: 'Eleanor Vance',
      email: 'eleanor.vance@example.com',
      phone: '13900010001',
      resume_file_path: null,
      resume_text: '8 年数据科学经验，熟悉 Python、机器学习和知识检索。',
      skills: ['Python', 'Machine Learning', 'Knowledge Graph', 'SQL'],
      experience_months: 96,
      available_from: '2026-08-01',
      source: 'MANUAL',
      profile_json: {},
      created_at: '2026-06-01T00:00:00Z',
      updated_at: '2026-06-15T00:00:00Z',
    },
    job_title: '首席数据科学家',
    current_stage: 'INTERVIEW_PENDING',
    score_total: 94,
  },
  {
    candidate: {
      id: 2,
      candidate_no: 'C-2026-002',
      full_name: 'Michael Chen',
      email: 'michael.chen@example.com',
      phone: '13900010002',
      resume_file_path: null,
      resume_text: '5 年前端开发经验，熟悉 Vue 3、TypeScript 和企业工作台。',
      skills: ['Vue 3', 'TypeScript', 'ECharts', 'CSS'],
      experience_months: 60,
      available_from: '2026-08-15',
      source: 'MANUAL',
      profile_json: {},
      created_at: '2026-06-05T00:00:00Z',
      updated_at: '2026-06-15T00:00:00Z',
    },
    job_title: '高级前端工程师',
    current_stage: 'AI_SCREENED',
    score_total: 91,
  },
];
