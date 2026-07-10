# 招聘多 Agent 评估

当前页面、组件、API 客户端和 SSE Composable 代码存在，待本地人工验收。当前运行范围只执行规则式招聘策略计划；其余五个节点以 `CURRENT_PHASE_NOT_IMPLEMENTED` 标记为 `SKIPPED`，不生成假结果。

共享 Agent 类型只来自 `src/shared/agent/contracts.ts`，真实请求和 SSE 客户端只来自 `src/shared/api/modules/agent.ts`。`api-contract.ts` 仅提供兼容类型重导出。

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

