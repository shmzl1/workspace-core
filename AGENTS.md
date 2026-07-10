# TalentFlow 根级协作约束

## 项目边界

- TalentFlow 智聘中枢是面向招聘决策、员工服务、考勤薪资预审与权限审计的可解释企业人力资源管理 Agent。
- 项目采用一套 FastAPI 后端，Vue Web 管理端、微信小程序员工端和 Gradio 内部调试台共享同一套 FastAPI 后端与业务 Service。
- 后端保持模块化单体，不采用微服务，不新增第二套后端。
- Gradio 仅用于内部 Agent 调试，不作为正式业务入口。
- 不引入 Redis、Celery、RabbitMQ、Kubernetes 或第二套后端，除非后续团队明确重新决策并更新 `.agent/decisions.md`。

## 分层调用

- 普通业务请求：`API -> Service -> Repository -> PostgreSQL`。
- 普通业务调用核心算法：`API -> Service -> human_only`。
- Agent 任务调用核心算法：`Agent -> Tool -> Service -> human_only`。
- RAG 问答：`Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- Route/API 不直接访问数据库。
- Route/API 不直接调用 `human_only`。
- Agent 不直接访问 Repository。
- Agent 不直接调用 `human_only`。
- 前端、小程序和 Gradio 不得直接访问数据库、禁飞区或底层算法。

## 分支与提交

- 只使用 `dev` 和 `main`。
- `dev` 是开发主线。
- `main` 是稳定版本分支。
- 禁止直接向 `main` 提交。
- 不使用 `feature/*` 分支流程。
- Commit 类型只使用 `feat`、`fix`、`docs`、`refactor`，并关联 Issue 或任务说明。

## AI 禁飞区

- `backend/app/human_only/resume_scoring.py`

- `backend/app/human_only/interview_scheduler.py`
- `backend/app/human_only/salary_access_control.py`
- `backend/tests/human_only/test_resume_scoring.py`
- `backend/tests/human_only/test_interview_scheduler.py`
- `backend/tests/human_only/test_salary_access_control.py`

保持纯 Python，不依赖 FastAPI、SQLAlchemy、LangGraph、ChromaDB、HTTP 客户端、数据库连接或 LLM。禁飞区只接收结构化输入，只输出结构化结果。

`human_only` 内部公开函数统一为：

- `score_resume(...)`
- `schedule_interview(...)`
- `check_salary_access(...)`

Service 层可以包装为：

- `score_candidates(...)`
- `generate_schedule(...)`
- `check_salary_access(...)`

Agent Tool 只能调用 Service 层函数，不能直接调用 `human_only` 函数。

## Agent 目录与事件约束

- `backend/app/agents/runtime/` 保存当前进程内 Runtime 与 SSE；`shared/` 保存公共契约；`workflows/` 保存工作流契约和静态节点元数据；`tools/` 只通过 Service 使用业务能力。
- `backend/app/rag/` 当前只提供 Schema 和 Protocol，不得把契约描述成真实检索。
- `backend/app/modules/recruitment/intelligence/` 只放分析契约；`services/` 同时保存真实 Run 上下文 Service 与未来专业 Service Protocol。
- Agent 文件不得访问 Repository 或直接导入 `human_only`；新 Tool 不得创建数据库 Session、访问 Repository 或直接导入 `human_only`。
- 前端不得伪造 Agent 日志、随机事件或固定延迟。`AGENT_THINKING` 仅表示可审计结构化阶段摘要，不得暴露隐藏思维链。
- 招聘 Agent 不自动录用或淘汰，面试 Agent 不确认排期，薪资预审助手不确认工资。
- 目录重构保留旧 import 兼容入口；未确认依赖迁移和测试前不得删除旧路径。
- 一个业务工作流一个目录；招聘工作流的每个顶层 Agent 当前对应一个 Python 文件，不提前拆成空子目录。
- Runtime 只负责 Run 生命周期、事件分发和 SSE，不承载业务 Repository 访问。
- 项目状态只写“代码存在，待本地人工验收”“已建立目录或契约”“计划中”。

## 默认执行规则

- 默认不运行 Conda、pip、npm、Docker、Git、数据库迁移、启动服务或构建命令。
- 允许在用户明确要求时执行只读检查、格式化、静态检查或测试。
- 不自动执行 `git push`、`git reset --hard`、`git clean -fd`、数据库迁移、Docker 启动、服务启动。
- 数据库迁移 `alembic upgrade head` 必须由人工确认后执行。
- 不创建真实 `.env` 文件。
- 不写入真实 API Key、Token、密码、数据库凭据或 JWT 密钥。
- 不提交真实上传文件、本地 Chroma 数据、真实报告和真实企业数据。
- 更改环境或者数据库结构必须给出组员用来同步更新的命令

## Agent 开发前检查清单

每次 Agent 修改前必须先确认：

- 当前任务属于哪个目录。
- 不新增第二套后端。
- 不绕过 Service。
- 涉及架构、接口、数据模型、权限、薪资预审、考勤、小程序范围变化时同步更新 docs 和 `.agent`。

## 文档同步

- 架构变化同步更新 `.agent/architecture.md` 和 `docs/架构设计.md`。
- 接口、表结构、规则、权限、薪资预审、考勤边界、小程序范围变化同步更新相关 docs。
- 技术决策变化同步更新 `.agent/decisions.md`。
