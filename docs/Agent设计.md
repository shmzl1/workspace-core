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

从简历和授权字段确定性提取 `CandidateProfile`、缺失项与 `ResumeEvidenceItem`。简历内指令只作为待分析文本，无证据的信息不得断言；代码存在，待本地人工验收。

## 5. 岗位匹配 Agent

依赖简历解析结果、岗位 Rubric、必备条件、企业知识来源及确定性评分 Service，输出 `JobMatchSummary`，`scoring_mode` 为 `DETERMINISTIC_HUMAN_ONLY`。Tool 只委托 Service，Service 通过既有 bridge 调用人工维护的 `score_resume(...)`；算法不可用时保留真实技能与证据，但不补造分数并标记人工复核。代码存在，待本地人工验收。

## 6. 面试评估 Agent

只允许读取真实结构化面试数据并输出 `InterviewEvaluationSummary`。当前工作流不执行无依据的智能面试分析；无真实结构化评价时以 `STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE` 标记为 `SKIPPED`，不得伪造技术、沟通或项目评价。当前已建立目录或契约。

## 7. 决策审查 Agent

按明确规则检查确定性评分、必备条件、证据覆盖、画像完整度、阈值和真实面试数据是否缺失，并确定性计算可信度，`review_mode` 为 `RULE_BASED_INTERMEDIATE`。缺少面试评价时继续执行并产生 `INTERVIEW_DATA_MISSING`；可以要求人工复核，但 `deterministic_score_preserved` 始终为 `true`。代码存在，待本地人工验收。

## 8. HR 最终报告

按确定性规则汇总招聘目标、候选人排名、审查结果、真实来源、人才缺口与下一步建议，`generation_mode` 为 `RULE_BASED_INTERMEDIATE`；有分候选人按分数降序且同分按编号升序，无分候选人排在最后。报告只表示建议和待复核状态，`requires_human_decision` 始终为 `true`，不拥有录用、淘汰、排期确认或薪资确认权。代码存在，待本地人工验收。

## 9. 员工服务 Agent

计划查询当前员工本人的考勤、年假、薪资摘要和制度。只能经 Tool 调用 Service，并保留权限与审计边界；当前已建立目录或契约，真实 Agent 执行为计划中。

## 10. 薪资预审助手

计划解释 Service 返回的预审结果、补贴、扣款和异常，只生成 HR 人工审查建议，不确认或修改工资；当前已建立目录或契约，真实助手执行为计划中。

## 11. Agent State

`AgentState` 保存 `run_id`、`trace_id`、创建用户、状态、当前节点、事件、来源和错误。招聘状态在此基础上保留真实 Run 上下文，并以默认空字段保存候选人画像、岗位匹配、面试评价、决策审查和 HR 报告。

## 12. Agent Event

`AgentEvent` 使用稳定大写枚举和 `snake_case` 字段。`AGENT_THINKING` 统一表示“可审计的结构化阶段摘要”，不得暴露隐藏思维链、完整简历、密码、JWT 或完整薪资。

## 13. Runtime 与 SSE

PostgreSQL Agent Run Store、六节点 LangGraph、Runner 兼容入口、数据库历史事件重放、进程内新增事件订阅、心跳和终止关闭代码存在，待本地人工验收。Run、State、Snapshot、节点、事件和 Tool 调用保存到 PostgreSQL；Graph State 只保存最小路由字段，SSE Subscriber Queue 只保存在当前进程。启动时将未终止的 `PENDING/RUNNING` Run 标记为 `FAILED`，错误码为 `AGENT_RUN_INTERRUPTED_BY_RESTART`，当前阶段不自动续跑。

## 14. Tool 边界

Agent 核心算法调用链为 `Agent -> Tool -> Service -> human_only`，纯规则审查与报告由 Tool 委托对应 Service。Agent 不访问 Repository 或 `human_only`；Tool 不创建新的数据库 Session，不直接访问 Repository 或 `human_only`。岗位匹配、决策审查和报告 Tool 的真实委托代码存在，待本地人工验收；现有员工 Tool 兼容入口在引用迁移前保留。

## 15. RAG 与来源

本地 Loader、结构化 Splitter、Provider-selected Embedding Client、ChromaDB Persistent Collection、Metadata 过滤、语义检索和关键词重排代码存在，待本地人工验收。`volcengine_multimodal` 使用火山方舟 `/embeddings/multimodal`，每个 Chunk 单独请求并保持返回顺序；禁用、初始化失败、检索失败或领域映射不足时明确回退，不记录密钥、完整文本或完整向量。

## 16. 可信度

Sprint 2.3 决策审查按 `0.4 × 证据覆盖 + 0.3 × 画像完整度 + 0.2 × 评分可用性 + 0.1 × 面试可用性` 计算可信度，结果限制在 0～100 并保留两位小数。可信度与人工维护的确定性评分分开显示，审查不得修改评分；代码存在，待本地人工验收。

## 17. 前端实时展示

`RecruitmentEvaluationPage`、集成状态面板、结果面板、流程板、事件流、节点详情、目标表单、Agent API 和 SSE Composable 代码存在，待本地人工验收。页面从 `/health` 读取 Run Store、LLM、RAG 和知识库计数，通过 URL 中的 `run_id` 恢复 PostgreSQL Snapshot 与历史事件；不得写死 READY、随机日志、固定延迟或静态事件。

## 18. 隐私与安全

事件与 Trace 只保存最小必要摘要；失败定位使用安全的 `failed_node` 和 `failed_step`，不记录异常原文、API Key、JWT、密码、数据库连接串、完整简历、完整联系方式或完整薪资。员工服务只能读取本人数据，HR 保留高影响决定权。

## 19. 降级策略

LLM、RAG 或人工评分算法不可用时，不生成假评分、假来源或假面试。人工评分算法不可用时岗位匹配返回无分结果并要求人工复核，规则式审查与结构化报告仍可继续；确定性评分、排期、考勤、薪资预审和权限能力保持独立。

## 20. 当前代码状态

| 状态 | 内容 |
| --- | --- |
| 代码存在，待本地人工验收 | PostgreSQL Run Store、六节点 LangGraph 编排、招聘策略、确定性简历解析、岗位匹配、规则式决策审查、LLM 叙述增强、ChromaDB RAG、SSE、Agent API、前端评估页面与 Composable |
| 已建立目录或契约 | 面试评估、招聘 intelligence、员工服务与薪资预审契约 |
| 计划中 | 真实面试评价 Agent、员工服务 Agent、薪资预审助手与 Gradio 执行 |

## 附录：当前 Sprint 2.3 代码细节

### Sprint 2.3 集成运行

```text
HR 提交真实岗位、候选人与企业招聘目标
→ RecruitmentRunContextService 校验投递关系
→ 创建 PostgreSQL Run 和真实 run_id
→ 招聘策略 Agent 生成 RecruitmentExecutionPlan
→ 企业知识 Tool 调用 RecruitmentKnowledgeService
→ 简历解析 Tool 逐候选人调用 ResumeProfileService
→ 岗位匹配 Tool 逐候选人调用 CandidateEvaluationService
→ 面试评估因无真实结构化评价标记为 SKIPPED
→ 决策审查 Tool 逐候选人调用 DecisionReviewService
→ 报告 Tool 调用 RecruitmentReportService
→ SSE 发布真实 AgentEvent
→ 前端增量更新工作流、来源、候选人画像、匹配、审查与报告
→ HR 人工决定
```

执行计划的 `executed_nodes` 固定为 `recruitment_strategy`、`resume_parser`、`job_match`、`decision_review`、`hr_report`，`skipped_nodes` 只包含 `interview_evaluation`。当前阶段为 `SPRINT_2_3_INTEGRATED`，下一阶段为 `END_TO_END_VALIDATION`。

岗位匹配使用人工维护的确定性评分算法；决策审查使用明确规则；HR 最终报告使用结构化汇总。无真实结构化面试评价时，面试评估以 `STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE` 跳过，决策审查继续执行并增加缺少真实面试评价的复核项。`NEEDS_REVIEW` 是合法业务结果，不会单独使工作流失败；报告正常生成后工作流可为 `COMPLETED`。

配置完整并初始化成功时，企业知识使用 `CHROMA_HYBRID`；否则使用 `LOCAL_HYBRID_FALLBACK`。招聘策略和 HR 报告先生成确定性结果，再通过 OpenAI-compatible Gateway 增强白名单叙述字段；模型不可用时使用 `RULE_BASED_FALLBACK`。Run 通过 PostgreSQL 恢复，代码存在，待本地迁移与人工验收。

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

- 当前状态：招聘策略、简历解析、岗位匹配、面试评估、决策审查和 HR 最终报告均为真实 LangGraph Node；完整入口与审核后报告入口共用同一 Graph 定义，代码存在，待本地人工验收。
- 面试评估：当前只保留契约；无真实结构化评价时跳过，不生成替代评价。
- 输入：企业招聘目标、真实岗位、真实候选人投递和 HR 操作上下文。
- 可调用 Tool：岗位 Service、候选人 Service、评分 Service、排期 Service、报告 Service。
- 不可调用 Tool：薪资确认、薪资修改、无权限薪资查询、禁飞区内部函数。
- 当前输出：`RecruitmentExecutionPlan`、`EnterpriseKnowledgeSummary`、`JobRubric`、`CandidateProfile`、`JobMatchSummary`、`DecisionReviewSummary`、`HRReportSummary`、真实 Run Snapshot 和 AgentEvent。
- Trace：保留候选人筛选条件、真实 Tool 调用、面试跳过原因和结构化解释摘要。
- RAG 来源：涉及制度或招聘规则时返回来源。
- 降级策略：核心算法未接入时不模拟算法结果，只提示待人工禁飞区接入。

正式节点职责如下：

| 节点 | 输入与依赖 | 输出 | 当前状态 |
| --- | --- | --- | --- |
| 招聘策略 | 已校验目标、岗位与候选人范围 | `RecruitmentExecutionPlan` | 代码存在，待本地人工验收 |
| 简历解析 | Service 白名单候选人字段、有限简历摘录、策略计划 | `CandidateProfile` 与证据 | 代码存在，待本地人工验收 |
| 岗位匹配 | 候选人画像、岗位 Rubric、确定性 Service 结果 | `JobMatchSummary` | 代码存在，待本地人工验收 |
| 面试评估 | 真实结构化面试数据 | `InterviewEvaluationSummary` | 已建立目录或契约；无真实数据时 `SKIPPED` |
| 决策审查 | 匹配结果、真实面试评价、来源 | `DecisionReviewSummary` | 代码存在，待本地人工验收 |
| HR 最终报告 | 招聘目标、审查结果、来源 | `HRReportSummary` | 代码存在，待本地人工验收 |

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

- Tool 保存 Service 边界、权限、敏感性和输入输出元数据；Sprint 2.3 的知识、简历、岗位匹配、决策审查和报告 Tool 只调用对应招聘 Service。
- RAG 包实现本地文档加载、稳定分块、可选择 Provider 的 Embedding、ChromaDB 持久化、Metadata 过滤与关键词重排；标准模型使用 `/embeddings`，`doubao-embedding-vision-251215` 使用 `/embeddings/multimodal`，HTTP 与响应错误只保留脱敏代码。
- 模型网关使用 `httpx.AsyncClient` 调用 OpenAI-compatible Chat Completions，只接入招聘策略和 HR 报告叙述增强，不改变确定性分数、排序、审查 findings 或最终人工决定。
- 招聘策略叙述增强与企业知识检索并行执行；两处叙述增强均关闭深度思考并限制输出 token。默认模型预算为招聘策略 25 秒、HR 最终报告 35 秒，超时后保留确定性基线并标记 `RULE_BASED_FALLBACK`；预算可通过 `AGENT_STRATEGY_MODEL_TIMEOUT_SECONDS` 和 `AGENT_REPORT_MODEL_TIMEOUT_SECONDS` 调整，相关代码存在，待本地人工验收。

### 可信度、隐私与降级

- 可信度后续按证据覆盖、画像完整度、Rubric 覆盖、知识相关度与 Agent 一致性分解，不用单一模型分数替代确定性评分。
- Trace 和 SSE 只保存最小必要的结构化摘要，不输出完整简历、完整薪资、隐藏思维链或无关敏感属性。
- LLM、ChromaDB 或 RAG 不可用时，Sprint 2.3 确定性核心继续独立工作；人工评分算法不可用时不补造分数，面试无真实数据时保持 `SKIPPED`，审查与报告只使用已有结构化事实。
- Agent 只提供事实、解释、审查与建议，HR 保留录用、淘汰、排期确认和薪资确认权。
