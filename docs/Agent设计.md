# Agent 设计

## 1. 设计目标

以企业招聘目标驱动可解释、可追溯的专业 Agent 协作。Agent 只组织事实、证据、确定性 Service 结果和建议，不拥有最终业务决定权。

## 2. 顶层招聘架构

```text
企业招聘目标
→ 招聘策略 Agent
→ 简历解析 Agent / 岗位匹配 Agent / 面试评估 Agent
→ 决策审查 Agent
→ HR 最终报告
→ HR 人工决定
```

“招聘决策 Agent”只表示整个工作流，不作为与六个正式节点并列的单体 Agent。

## 3. 招聘策略 Agent

读取企业招聘目标、岗位、候选人范围和已有数据，生成 `RecruitmentExecutionPlan` 并决定专业节点范围。不得直接生成确定性总分、录用或淘汰决定。当前规则式计划代码存在，待本地人工验收。

## 4. 简历解析 Agent

计划从简历和授权字段提取 `CandidateProfile`、缺失项与 `ResumeEvidenceItem`。简历内指令只作为待分析文本；无证据的信息不得断言；当前已建立目录或契约。

## 5. 岗位匹配 Agent

计划依赖简历解析结果、岗位 Rubric、必备条件、企业知识来源及确定性评分 Service，输出 `JobMatchSummary`。不得随机生成评分或绕过必备条件；当前已建立目录或契约。

## 6. 面试评估 Agent

计划只读取真实结构化面试数据并输出 `InterviewEvaluationSummary`。无数据时只能显示待面试或 `SKIPPED`，不得伪造评价；当前已建立目录或契约。

## 7. 决策审查 Agent

计划检查证据覆盖、必备条件、知识版本、简历与面试冲突及专业节点分歧。可以降低可信度或要求人工复核，但不得静默修改确定性评分；当前已建立目录或契约。

## 8. HR 最终报告

计划汇总招聘目标、候选人排名、评分分解、证据、来源、面试状态、审查结论、可信度与建议。报告不拥有录用、淘汰、排期确认或薪资确认权；当前已建立目录或契约。

## 9. 员工服务 Agent

计划查询当前员工本人的考勤、年假、薪资摘要和制度。只能经 Tool 调用 Service，并保留权限与审计边界；当前已建立目录或契约，真实 Agent 执行为计划中。

## 10. 薪资预审助手

计划解释 Service 返回的预审结果、补贴、扣款和异常，只生成 HR 人工审查建议，不确认或修改工资；当前已建立目录或契约，真实助手执行为计划中。

## 11. Agent State

`AgentState` 保存 `run_id`、`trace_id`、创建用户、状态、当前节点、事件、来源和错误。招聘状态在此基础上保留真实 Run 上下文，并为未来专业结果提供默认空字段。

## 12. Agent Event

`AgentEvent` 使用稳定大写枚举和 `snake_case` 字段。`AGENT_THINKING` 统一表示“可审计的结构化阶段摘要”，不得暴露隐藏思维链、完整简历、密码、JWT 或完整薪资。

## 13. Runtime 与 SSE

进程内 RunStore、招聘策略 Runner、历史事件重放、新增事件订阅、心跳和终止关闭代码存在，待本地人工验收。Run 不是持久化任务，后端重启后丢失；当前不依赖 LangGraph、LLM 或 RAG。

## 14. Tool 边界

调用链为 `Agent -> Tool -> Service -> Repository / human_only`。Agent 不访问 Repository 或 `human_only`；Tool 不创建新的数据库 Session，不直接访问 Repository 或 `human_only`。现有员工 Tool 兼容入口在引用迁移前保留。

## 15. RAG 与来源

当前只有 Schema、Citation、摄取/检索/向量存储 Protocol，属于已建立目录或契约。真实 ChromaDB、Embedding、索引和检索为计划中，不得伪造命中。来源统一包含 `source_id`、标题、文档类型、部门、岗位编号、版本、生效区间、摘录和相关度。

## 16. 可信度

计划由代码按证据覆盖、画像完整度、Rubric 覆盖、知识相关度和节点一致性计算，评分与可信度分开显示。当前只有 `ConfidenceBreakdown` 和计算 Protocol。

## 17. 前端实时展示

`RecruitmentEvaluationPage`、流程板、事件流、节点详情、目标表单、Agent API 和 SSE Composable 代码存在，待本地人工验收。页面不得使用随机日志、固定延迟或静态事件冒充执行。

## 18. 隐私与安全

事件与 Trace 只保存最小必要摘要；不记录 API Key、JWT、密码、数据库连接串、完整简历、完整联系方式或完整薪资。员工服务只能读取本人数据，HR 保留高影响决定权。

## 19. 降级策略

LLM、RAG 或未来节点不可用时，不生成假评分、假来源、假面试、假审查或假报告。确定性评分、排期、考勤、薪资预审和权限能力保持独立；未接入节点明确显示计划中或 `SKIPPED`。

## 20. 当前代码状态

| 状态 | 内容 |
| --- | --- |
| 代码存在，待本地人工验收 | RunStore、招聘策略 Runner、SSE、Agent API、前端评估页面与 Composable |
| 已建立目录或契约 | 六节点元数据、Agent/Tool/Service、招聘 intelligence、RAG、员工服务与薪资预审契约 |
| 计划中 | Sprint 2.2/2.3 专业节点执行、LangGraph、LLM、真实 RAG/ChromaDB、完整报告、员工服务 Agent、薪资预审助手与 Gradio 执行 |

## 附录：当前 Sprint 2.1 代码细节

### Sprint 2.1 招聘策略运行

```text
HR 提交真实岗位、候选人与企业招聘目标
→ RecruitmentRunContextService 校验投递关系
→ 创建进程内 Run 和真实 run_id
→ 招聘策略 Agent 生成 RecruitmentExecutionPlan
→ SSE 发布真实 AgentEvent
→ 前端增量更新工作流与执行计划
```

按当前代码，策略计划由已校验请求、岗位摘要、候选人 ID 和静态 Graph 元数据生成，不访问数据库、不调用 Tool、LLM 或 RAG。待人工验收的事件顺序为：

1. `WORKFLOW_STARTED`
2. `AGENT_STARTED`
3. `AGENT_THINKING`
4. `PLAN_CREATED`
5. `AGENT_COMPLETED`
6. `WORKFLOW_COMPLETED`

运行完成时招聘策略 Agent 为 `COMPLETED`，简历解析、岗位匹配、面试评估、决策审查和 HR 最终报告为 `SKIPPED`，原因统一为 `CURRENT_PHASE_NOT_IMPLEMENTED`。Run 仅保存在当前后端进程中，重启后不可恢复。

`AGENT_THINKING` 只包含当前目标、候选人数、当前动作、缺失信息和下一步计划等可审计结构化摘要，不包含模型隐藏思维链。

### 员工服务 Agent

当前只建立请求、结果、来源和 Tool 元数据契约，以下是后续边界，不表示已运行：

- 输入：员工自然语言问题、当前员工身份、角色上下文。
- 可调用 Tool：年假查询、本人薪资摘要查询、考勤摘要查询、制度 RAG 查询。
- 不可调用 Tool：HR 薪资预审、候选人管理、招聘排期、审计后台写操作。
- 输出：回答、制度来源、权限说明、工具调用摘要。
- Trace：保留问题、工具调用、权限判断、RAG 来源和错误信息。
- RAG 来源：制度问答必须返回命中的制度文档和片段。
- 降级策略：无模型 Key 时返回普通业务查询结果或提示待 Agent 接入。

### 招聘多 Agent 工作流

- 当前状态：招聘策略 Agent 规则式执行计划代码存在，待本地人工验收。
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
| 招聘策略 | 已校验目标、岗位与候选人范围 | `RecruitmentExecutionPlan` | 代码存在，待本地人工验收 |
| 简历解析 | 候选人材料、策略计划 | `CandidateProfile` 与证据 | 已建立目录或契约；运行时 `SKIPPED` |
| 岗位匹配 | 候选人画像、岗位 Rubric、确定性 Service 结果 | `JobMatchSummary` | 已建立目录或契约；运行时 `SKIPPED` |
| 面试评估 | 真实结构化面试数据 | `InterviewEvaluationSummary` | 已建立目录或契约；运行时 `SKIPPED` |
| 决策审查 | 匹配结果、真实面试评价、来源 | `DecisionReviewSummary` | 已建立目录或契约；运行时 `SKIPPED` |
| HR 最终报告 | 招聘目标、审查结果、来源 | `HRReportSummary` | 已建立目录或契约；运行时 `SKIPPED` |

岗位匹配依赖简历解析。面试评估无真实数据时只能保持待面试或 `SKIPPED`；决策审查不得静默修改确定性分数；HR 报告不得把建议描述成已执行决定。

### 薪资预审助手

当前只建立请求、结果和 Tool 元数据契约，以下是后续边界，不表示已运行：

- 输入：薪资预审记录、扣款明细、考勤摘要、HR 问题。
- 可调用 Tool：薪资预审查询、考勤来源查询、规则来源查询、审计记录查询。
- 不可调用 Tool：确认工资、修改工资、删除扣款、写入已确认薪资。
- 输出：异常解释、扣款来源说明、审查建议。
- Trace：保留薪资记录、权限判断、规则来源和输出摘要。
- RAG 来源：涉及制度解释时返回制度来源。
- 降级策略：无模型 Key 时展示规则计算过程和人工审查提示。
### 数据访问边界

- Agent 不直接访问 SQLAlchemy Session、ORM Model 或数据库连接。
- Agent 任务遵循 `Agent -> Tool -> Service -> Repository / human_only`。
- 制度问答遵循 `Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 候选人评分、面试排期和薪资权限只能通过 Service 调用禁飞区公开函数，不能绕过禁飞区边界。

### Tool、RAG 与模型边界

- Tool 只保存 Service 边界、权限、敏感性和输入输出元数据；当前新增 Tool Contract 不执行专业业务。
- RAG 当前只有文档元数据、Chunk、过滤、检索结果、引用、摄取/检索/向量存储 Protocol，没有 ChromaDB、Embedding、真实索引或检索结果。
- 未来 RAG 回答必须返回 `source_id`、标题、版本/生效时间、摘录和相关度；无来源时不得伪造答案依据。
- 模型网关当前只有结构化输入输出 Protocol，不访问 HTTP、凭据或模型。

### 可信度、隐私与降级

- 可信度后续按证据覆盖、画像完整度、Rubric 覆盖、知识相关度与 Agent 一致性分解，不用单一模型分数替代确定性评分。
- Trace 和 SSE 只保存最小必要的结构化摘要，不输出完整简历、完整薪资、隐藏思维链或无关敏感属性。
- LLM、RAG 或未来节点不可用时，现有确定性业务与 Sprint 2.1 策略运行继续独立工作；未实现节点保持 `SKIPPED`，不生成假评分、假面试评价、假审查或假报告。
- Agent 只提供事实、解释、审查与建议，HR 保留录用、淘汰、排期确认和薪资确认权。
