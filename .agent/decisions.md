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
