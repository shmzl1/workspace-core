# TalentFlow 技术决策记录

## ADR-001：采用模块化单体，不使用微服务

- 状态：已接受
- 决策：后端采用 FastAPI 模块化单体。
- 原因：团队规模和周期更适合清晰模块边界、简单部署和快速联调。
- 影响：不引入微服务治理、跨服务通信、Redis、Celery、RabbitMQ 或 Kubernetes，除非后续团队明确重新决策并更新本文档。

## ADR-002：Web、小程序、Gradio 共用 FastAPI

- 状态：已接受
- 决策：Vue Web 管理端、微信小程序员工端和 Gradio 内部调试台共享一套 FastAPI 后端。
- 原因：避免第二套后端和重复业务逻辑。
- 影响：所有端必须复用统一 API、Service 和权限上下文；前端、小程序和 Gradio 不直接访问数据库、禁飞区或底层算法。

## ADR-003：考勤作为独立模块

- 状态：已接受
- 决策：考勤独立为 `attendance` 模块。
- 原因：考勤事实会被员工端、HR 汇总和薪资预审共同读取。
- 影响：payroll 只读取考勤事实和月度汇总，不反向修改原始考勤记录。

## ADR-004：薪资预审与 HR 确认分离

- 状态：已接受
- 决策：薪资预审由规则引擎计算，AI 只解释和建议，HR 最终确认。
- 原因：薪资属于高敏感数据，必须保留人工确认和审计链路。
- 影响：Agent 不得确认工资、修改工资、删除扣款或写入已确认薪资。

## ADR-005：小程序只接员工简单功能

- 状态：已接受
- 决策：小程序一期只做员工首页、签到签退、考勤摘要、年假、本人薪资摘要和制度查询。
- 原因：控制范围，避免把 HR 管理后台迁入小程序。
- 影响：小程序不得调用 HR 招聘、排期、薪资预审和审计后台接口。

## ADR-006：采用分层 AGENTS.md 约束

- 状态：已接受
- 决策：在根目录、docs、backend、frontend、miniprogram、Agent、payroll 和禁飞区目录设置 AGENTS.md。
- 原因：用目录级约束防止误改禁飞区、误扩架构和误生成第二套后端。
- 影响：后续开发需遵守最接近目录的 AGENTS.md。

## ADR-007：只使用 dev 和 main 分支

- 状态：已接受
- 决策：协作分支只使用 `dev` 和 `main`。
- 原因：课程团队周期短，简化合并和验收路径。
- 影响：`dev` 是开发主线，`main` 是稳定版本分支；禁止直接向 `main` 提交；文档和协作规范中不再使用 `feature/*` 分支流程。

## ADR-008：建立 SQLAlchemy 2.0 ORM 与 Alembic 首次迁移

- 状态：已接受
- 决策：使用 SQLAlchemy 2.0 风格 ORM 描述初始数据库模型，并用 Alembic 手写 `0001_initial_schema` 首次迁移。
- 原因：项目需要可追踪的数据库结构变更，避免在应用启动时隐式建表。
- 影响：禁止使用 `Base.metadata.create_all` 初始化业务表；后续表结构变化必须新增或修改 Alembic 迁移，并同步数据库设计文档。

## ADR-009：业务状态使用 String 与 CheckConstraint

- 状态：已接受
- 决策：初始模型中的业务状态字段使用 `String` 加 `CheckConstraint`，不使用 PostgreSQL Enum。
- 原因：课程项目阶段状态可能调整，字符串约束比数据库枚举更易迁移和回滚。
- 影响：新增状态时需要同步 ORM、迁移、接口契约和相关文档。

## ADR-010：初始迁移不包含种子数据

- 状态：已接受
- 决策：`0001_initial_schema` 只创建结构，不插入账号、员工、候选人、制度、薪资或演示数据。
- 原因：结构迁移和演示数据应分离，避免真实数据、课程演示数据和数据库结构耦合。
- 影响：后续如需演示数据，应在独立 seed 脚本或数据文档中处理，不混入 Alembic 结构迁移。

## ADR-011：统一分层调用链

- 状态：已接受
- 决策：普通业务请求使用 `API -> Service -> Repository -> PostgreSQL`；普通业务调用核心算法使用 `API -> Service -> human_only`；Agent 任务调用核心算法使用 `Agent -> Tool -> Service -> human_only`；RAG 问答使用 `Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 原因：明确 Route、Service、Repository、Agent、RAG 和禁飞区职责，避免越层调用。
- 影响：Route/API 不直接访问数据库或 `human_only`；Agent 不直接访问 Repository 或 `human_only`。

## ADR-012：统一禁飞区公开函数入口

- 状态：已接受
- 决策：`human_only` 内部公开函数统一为 `score_resume(...)`、`schedule_interview(...)`、`check_salary_access(...)`；Service 层可以包装为 `score_candidates(...)`、`generate_schedule(...)`、`check_salary_access(...)`。
- 原因：区分纯算法入口和工程 Service 入口，减少 Agent Tool 误调用禁飞区的风险。
- 影响：Agent Tool 只能调用 Service 层函数，不能直接调用 `human_only` 函数；AI 不得创建、修改、移动、删除、格式化、补全禁飞区核心实现和核心测试。

## ADR-013：命令执行默认保守

- 状态：已接受
- 决策：默认不运行 Conda、pip、npm、Docker、Git、数据库迁移、启动服务或构建命令；用户明确要求时可以执行只读检查、格式化、静态检查或测试。
- 原因：避免在课程项目初始化阶段误启动服务、误迁移数据库或误推送 Git。
- 影响：不自动执行 `git push`、`git reset --hard`、`git clean -fd`、数据库迁移、Docker 启动、服务启动；`alembic upgrade head` 必须由人工确认后执行。

## ADR-014：JWT 与数据库权限字段作为统一授权来源

- 状态：已接受
- 决策：业务请求使用 JWT 确认账号身份，并在每次请求从 `users.permissions` 读取最新权限；角色保留用于展示、审计和账号初始化。
- 原因：前端角色切换和请求 Header 不能作为可信授权来源，权限调整也应能在不重发 Token 的情况下生效。
- 影响：业务接口通过统一权限依赖返回 401 或 403；前端仅用权限隐藏入口，不能替代后端数据范围校验。

## ADR-015：招聘采用总控加专业 Agent 架构

- 状态：已接受
- 决策：企业招聘目标 → 招聘策略 Agent → 简历解析 Agent / 岗位匹配 Agent / 面试评估 Agent → 决策审查 Agent → HR 最终报告 → HR 人工决定。
- 原因：把规划、事实提取、岗位匹配、真实面试评价和审查分离，保留证据与责任边界。
- 影响：Sprint 2.2 执行招聘策略和确定性简历解析节点；岗位匹配及后续节点目前仅有契约。岗位匹配依赖简历解析，无真实面试数据时面试评估必须跳过。

## ADR-016：Agent 运行过程通过结构化 SSE 事件展示

- 状态：已接受
- 决策：Sprint 2.2 的 SSE、`AgentEvent` 和前端展示代码存在，待本地人工验收；事件只展示可审计阶段摘要。
- 原因：支持实时可视化与审计，同时保护隐私和模型内部推理。
- 影响：SSE 先从 PostgreSQL 重放历史事件，再发送当前进程 Queue 中的新增事件，使用 `event: agent_event` 并支持心跳；前端不伪造日志，`AGENT_THINKING` 不暴露隐藏思维链。

## ADR-017：Agent 不拥有最终业务决策权

- 状态：已接受
- 决策：Agent 不自动录用、淘汰、确认排期或确认薪资，HR 保留最终决定。
- 原因：招聘、面试与薪资属于高影响业务，需要人工确认与审计。
- 影响：Agent 输出只作为结构化事实、审查结果和建议。

## ADR-018：目录重构采用兼容迁移

- 状态：已接受
- 决策：新增 `shared/workflows/tools` 等目录，旧路径保留兼容重导出，同一阶段不删除仍被调用的旧入口。
- 原因：避免破坏现有 Runtime、Sprint 1 import 和业务行为。
- 影响：旧文件只能在所有 import 迁移且相关测试通过后由团队删除；新契约字段必须提供兼容默认值。

## ADR-019：实现状态与人工验收状态分离

- 状态：已接受
- 决策：项目文档只使用“代码存在，待本地人工验收”“已建立目录或契约”“计划中”描述当前状态。
- 原因：文件和 Route 存在不能替代本地运行、权限、联调、测试或部署验收。
- 影响：RunStore、SSE、Agent API 和前端评估页面不得直接写成已验收通过；Schema、Protocol 或目录不得写成真实业务能力。

## ADR-020：Sprint 2.2 企业知识采用可声明的本地回退

- 状态：已由 ADR-022 扩展，保留为故障回退
- 决策：在 ChromaDB、Embedding 和 LLM 尚未接入时，招聘知识由 `Agent -> Tool -> RecruitmentKnowledgeService` 执行结构化过滤加关键词相关度的本地回退，并在契约中明确返回 `LOCAL_HYBRID_FALLBACK`。
- 原因：Sprint 2.2 需要真实、可审计的岗位标准与来源，同时不能把静态契约或本地数据伪装成向量检索。
- 影响：来源必须携带岗位/部门、文档类型、版本、生效日期、有限摘录和相关度；`backend/app/rag/` 继续只保存 Schema/Protocol。未来接入真实 ChromaDB 时必须新增明确运行模式并保持当前来源契约兼容。

## ADR-021：异步集成网关与应用级依赖注入

- 状态：已由 ADR-022 落实
- 决策：ModelGateway 和 RetrievalGateway 使用异步接口，由 ApplicationContainer 统一组装并通过 RecruitmentRunnerDependencies 注入 Runner。当前确定性本地知识回退继续保留。
- 原因：真实模型、Embedding 和 ChromaDB 尚未实现，需要先建立无网络副作用、可检查状态且不影响确定性业务的稳定边界。
- 影响：真实模型计划通过 `httpx` 调用 OpenAI 兼容 API，本地知识库计划使用 ChromaDB 持久化；LangChain 和 LangGraph 不是连通前置条件。LLM/RAG 故障不得影响确定性业务，真实检索失败时允许明确回退到 `LOCAL_HYBRID_FALLBACK`，健康接口不返回凭证。

## ADR-022：持久化 Agent Runtime 并接入 OpenAI-compatible LLM 与 ChromaDB

- 状态：已接受，代码存在，待本地人工验收
- 决策：Agent Run、节点、事件和 Tool 调用保存到 PostgreSQL，SSE Queue 继续保留在当前进程；招聘策略与 HR 报告仅在确定性结果生成后使用 OpenAI-compatible Gateway 增强白名单叙述字段；企业知识按配置选择标准 OpenAI-compatible Embedding 或火山方舟多模态 Embedding Client，并使用 ChromaDB Persistent Collection、Metadata 过滤和关键词重排。
- 原因：支持后端重启后按 `run_id` 恢复审计结果，同时让模型和知识库成为可关闭、可降级的增强能力，不改变人工算法和 HR 最终决定权。
- 影响：新增 `0004_agent_runtime` 迁移；LLM/RAG 失败时分别使用 `RULE_BASED_FALLBACK` 和 `LOCAL_HYBRID_FALLBACK`；健康接口返回安全状态和知识库计数，不返回密钥、连接串、文档全文或模型原始响应。
