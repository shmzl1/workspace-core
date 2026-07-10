# 招聘多 Agent 评估

当前页面、组件、API 客户端和 SSE Composable 代码存在，待本地人工验收。当前运行范围执行规则式招聘策略、企业知识本地回退与确定性简历解析；岗位匹配及后续四个节点以 `CURRENT_PHASE_NOT_IMPLEMENTED` 标记为 `SKIPPED`，不生成假结果。

共享 Agent 类型只来自 `src/shared/agent/contracts.ts`，真实请求和 SSE 客户端只来自 `src/shared/api/modules/agent.ts`。`types.ts` 与 `api-contract.ts` 仅作为已弃用兼容重导出保留，不维护第二份契约。

Sprint 2.2 页面包括真实运行总体状态、流程板、事件流、按节点过滤的详情，以及策略、企业知识来源和候选人画像/证据面板。当前只执行招聘策略、企业知识本地混合回退和确定性简历解析；岗位匹配及后续节点显示 `SKIPPED`，不创建占位事件或虚构评分。

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

