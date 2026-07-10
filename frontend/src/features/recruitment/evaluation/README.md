# 招聘多 Agent 评估

当前页面、组件、API 客户端和 SSE Composable 代码存在，待本地人工验收。当前运行范围只执行规则式招聘策略计划；其余五个节点以 `CURRENT_PHASE_NOT_IMPLEMENTED` 标记为 `SKIPPED`，不生成假结果。

共享 Agent 类型只来自 `src/shared/agent/contracts.ts`，真实请求和 SSE 客户端只来自 `src/shared/api/modules/agent.ts`。`types.ts` 与 `api-contract.ts` 仅作为已弃用兼容重导出保留，不维护第二份契约。

Sprint 2.1 页面包括真实运行总体状态、流程板、事件流和按节点过滤的详情。无 Tool、RAG、候选人处理或专业节点结果时显示明确的未调用、未检索、未处理或 `SKIPPED` 状态，不创建占位事件。

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

