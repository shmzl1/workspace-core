# 招聘多 Agent 评估

当前页面、集成状态、API 客户端、Run 恢复和 SSE Composable 代码存在，待本地人工验收。页面通过 `/health` 展示 PostgreSQL Run Store、LLM、RAG、文档数和 Chunk 数；通过 `?run_id=` 从后端恢复 Snapshot 与历史事件，不伪造 READY 或 Agent 事件。

共享 Agent 类型只来自 `src/shared/agent/contracts.ts`，真实请求和 SSE 客户端只来自 `src/shared/api/modules/agent.ts`。`types.ts` 与 `api-contract.ts` 仅作为已弃用兼容重导出保留，不维护第二份契约。

页面包括集成状态、真实运行总体状态、流程板、事件流、按节点过滤的详情，以及策略、企业知识来源、候选人画像、岗位匹配、决策审查和 HR 报告。面试评价仅在存在真实结构化反馈时执行，不创建占位事件或虚构评分。

计划中的最终组件：

- `RecruitmentGoalPanel`
- `RecruitmentStrategyCard`
- `MultiAgentWorkflowBoard`
- `AgentRealtimeFeed`
- `ResumeParserAgentCard`
- `JobMatchAgentCard`
- `InterviewEvaluationAgentCard`
- `DecisionReviewCard`
- `EvidencePanel`
- `KnowledgeSourcesPanel`
- `ConfidenceBreakdown`
- `CandidateComparisonMatrix`
- `HRFinalReportPanel`

列表仅表示计划中，不代表组件均已创建或功能已实现。

