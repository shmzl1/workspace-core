# Agent 设计

本文记录 Agent 边界与当前实现状态。Sprint 2.1 已真实运行招聘策略 Agent；不表示其他 Agent、LangGraph、LLM 或 RAG 已完成。

## 实现状态分层

| 状态 | 内容 |
| --- | --- |
| 已实现 | 真实岗位与投递校验、招聘策略规则式计划、进程内 RunStore、真实 `run_id`/`trace_id`、SSE、前端实时流程看板 |
| 已建立契约 | 六节点静态图、Agent/Tool/Service 边界、候选人证据与审查类型、RAG Schema/Protocol、来源引用和模型网关类型 |
| 后续规划 | LangGraph、LLM、真实 RAG/ChromaDB、其余五个招聘节点、员工服务 Agent、薪资预审助手和 Gradio Agent 执行 |

## Sprint 2.1 招聘策略运行

```text
HR 提交真实岗位、候选人与企业招聘目标
→ RecruitmentRunContextService 校验投递关系
→ 创建进程内 Run 和真实 run_id
→ 招聘策略 Agent 生成 RecruitmentExecutionPlan
→ SSE 发布真实 AgentEvent
→ 前端增量更新工作流与执行计划
```

策略计划完全由已校验请求、真实岗位摘要、候选人 ID 和静态 Graph 元数据生成，不访问数据库、不调用 Tool、LLM 或 RAG。真实事件顺序为：

1. `WORKFLOW_STARTED`
2. `AGENT_STARTED`
3. `AGENT_THINKING`
4. `PLAN_CREATED`
5. `AGENT_COMPLETED`
6. `WORKFLOW_COMPLETED`

运行完成时招聘策略 Agent 为 `COMPLETED`，简历解析、岗位匹配、面试评估、决策审查和 HR 最终报告为 `SKIPPED`，原因统一为 `CURRENT_PHASE_NOT_IMPLEMENTED`。Run 仅保存在当前后端进程中，重启后不可恢复。

`AGENT_THINKING` 只包含当前目标、候选人数、当前动作、缺失信息和下一步计划等可审计结构化摘要，不包含模型隐藏思维链。

## 员工服务 Agent

当前只建立请求、结果、来源和 Tool 元数据契约，以下是后续边界，不表示已运行：

- 输入：员工自然语言问题、当前员工身份、角色上下文。
- 可调用 Tool：年假查询、本人薪资摘要查询、考勤摘要查询、制度 RAG 查询。
- 不可调用 Tool：HR 薪资预审、候选人管理、招聘排期、审计后台写操作。
- 输出：回答、制度来源、权限说明、工具调用摘要。
- Trace：保留问题、工具调用、权限判断、RAG 来源和错误信息。
- RAG 来源：制度问答必须返回命中的制度文档和片段。
- 降级策略：无模型 Key 时返回普通业务查询结果或提示待 Agent 接入。

## 招聘多 Agent 工作流

- 当前已实现：招聘策略 Agent 规则式执行计划。
- 后续节点：简历解析 Agent、岗位匹配 Agent、面试评估 Agent、决策审查 Agent、HR 最终报告。
- 输入：企业招聘目标、真实岗位、真实候选人投递和 HR 操作上下文。
- 可调用 Tool：岗位 Service、候选人 Service、评分 Service、排期 Service、报告 Service。
- 不可调用 Tool：薪资确认、薪资修改、无权限薪资查询、禁飞区内部函数。
- 当前输出：`RecruitmentExecutionPlan`、真实 Run Snapshot 和 AgentEvent。
- Trace：保留候选人筛选条件、评分调用、排期调用和解释摘要。
- RAG 来源：涉及制度或招聘规则时返回来源。
- 降级策略：核心算法未接入时不模拟算法结果，只提示待人工禁飞区接入。

正式节点职责如下：

| 节点 | 输入与依赖 | 输出 | 当前状态 |
| --- | --- | --- | --- |
| 招聘策略 | 已校验目标、岗位与候选人范围 | `RecruitmentExecutionPlan` | 已规则式执行 |
| 简历解析 | 候选人材料、策略计划 | `CandidateProfile` 与证据 | 仅契约，`SKIPPED` |
| 岗位匹配 | 候选人画像、岗位 Rubric、确定性 Service 结果 | `JobMatchSummary` | 仅契约，`SKIPPED` |
| 面试评估 | 真实结构化面试数据 | `InterviewEvaluationSummary` | 仅契约，`SKIPPED` |
| 决策审查 | 匹配结果、真实面试评价、来源 | `DecisionReviewSummary` | 仅契约，`SKIPPED` |
| HR 最终报告 | 招聘目标、审查结果、来源 | `HRReportSummary` | 仅契约，`SKIPPED` |

岗位匹配依赖简历解析。面试评估无真实数据时只能保持待面试或 `SKIPPED`；决策审查不得静默修改确定性分数；HR 报告不得把建议描述成已执行决定。

## 薪资预审助手

当前只建立请求、结果和 Tool 元数据契约，以下是后续边界，不表示已运行：

- 输入：薪资预审记录、扣款明细、考勤摘要、HR 问题。
- 可调用 Tool：薪资预审查询、考勤来源查询、规则来源查询、审计记录查询。
- 不可调用 Tool：确认工资、修改工资、删除扣款、写入已确认薪资。
- 输出：异常解释、扣款来源说明、审查建议。
- Trace：保留薪资记录、权限判断、规则来源和输出摘要。
- RAG 来源：涉及制度解释时返回制度来源。
- 降级策略：无模型 Key 时展示规则计算过程和人工审查提示。
## 数据访问边界

- Agent 不直接访问 SQLAlchemy Session、ORM Model 或数据库连接。
- Agent 任务遵循 `Agent -> Tool -> Service -> Repository / human_only`。
- 制度问答遵循 `Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 候选人评分、面试排期和薪资权限只能通过 Service 调用禁飞区公开函数，不能绕过禁飞区边界。

## Tool、RAG 与模型边界

- Tool 只保存 Service 边界、权限、敏感性和输入输出元数据；当前新增 Tool Contract 不执行专业业务。
- RAG 当前只有文档元数据、Chunk、过滤、检索结果、引用、摄取/检索/向量存储 Protocol，没有 ChromaDB、Embedding、真实索引或检索结果。
- 未来 RAG 回答必须返回 `source_id`、标题、版本/生效时间、摘录和相关度；无来源时不得伪造答案依据。
- 模型网关当前只有结构化输入输出 Protocol，不访问 HTTP、凭据或模型。

## 可信度、隐私与降级

- 可信度后续按证据覆盖、画像完整度、Rubric 覆盖、知识相关度与 Agent 一致性分解，不用单一模型分数替代确定性评分。
- Trace 和 SSE 只保存最小必要的结构化摘要，不输出完整简历、完整薪资、隐藏思维链或无关敏感属性。
- LLM、RAG 或未来节点不可用时，现有确定性业务与 Sprint 2.1 策略运行继续独立工作；未实现节点保持 `SKIPPED`，不生成假评分、假面试评价、假审查或假报告。
- Agent 只提供事实、解释、审查与建议，HR 保留录用、淘汰、排期确认和薪资确认权。
