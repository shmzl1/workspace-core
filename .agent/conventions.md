# TalentFlow 智聘中枢协作规范

## 分支策略

- `main`：稳定分支，只接收 Sprint 验收后的合并。
- `dev`：开发主线，所有功能先合入该分支。
- `feature/*`：功能分支，按 Issue 或功能模块创建，例如 `feature/recruitment-board`。

## Commit 规范

- Commit 格式严格使用以下四类：
  - `feat: 简述`
  - `fix: 简述`
  - `docs: 简述`
  - `refactor: 简述`
- 每次提交必须关联 Issue，在提交说明或 Pull Request 中写明 Issue 编号。
- 禁止使用无法说明变更目的的提交信息，例如 `update`、`temp`、`misc`。

## 合并规则

- 功能分支先合入 `dev`。
- Sprint 验收后，再由 `dev` 合入 `main`。
- 禁止直接向 `main` 提交代码。
- 涉及架构、禁飞区、权限或 Agent 调用链的改动，合并前必须补充决策记录。

## 前端规范

- 正式前端使用 Vue 3 + TypeScript + Vite。
- 企业 SaaS 工作台结构包括左侧模块导航栏、顶部全局操作区、中间业务工作区和底部全局 Agent 指令栏。
- Vue 组件按功能模块放入 `frontend/src/features/`。
- 通用组件放入 `frontend/src/components/`。
- 全局布局放入 `frontend/src/layouts/`。
- 页面交互优先使用 Element Plus；图表使用 ECharts；日历使用 FullCalendar；拖拽排序使用 `vuedraggable`；HTTP 调用使用 Axios；Agent 流式响应使用 SSE。

## 后端规范

- 后端使用 Python 3.12 + FastAPI + Pydantic + SQLAlchemy + Alembic。
- FastAPI 采用模块化单体，不拆分微服务。
- API 层、Service 层、Repository 层、Agent 层、RAG 层和 `human_only` 层职责分离。
- API 层只负责请求校验、鉴权入口、响应封装和调用 Service 或 Agent。
- Service 层负责业务编排和权限检查。
- Repository 层负责数据库读写。
- Agent 层负责 LangGraph 流程编排。
- RAG 层负责制度知识库检索、来源组织和上下文拼装。
- `human_only` 层只保存人工手写核心算法，不直接依赖 Web、数据库、Agent 或大模型框架。

## Agent 规范

- 简单、确定性的 CRUD 操作不走 Agent，直接走普通业务 API。
- 自然语言任务、多工具任务、跨模块任务才走 LangGraph Agent。
- Agent 调用核心算法必须遵循 `Tool -> Service -> human_only` 调用链。
- Agent 不得绕过 Service 层权限检查，不得直接访问 `human_only` 内部实现。
- Agent 过程需要保留工具调用、RAG 命中内容、错误信息和关键中间结果，便于 Gradio 调试台查看。

## AI 使用规范

- AI 可辅助生成非禁飞区工程代码、页面、接口、测试骨架和文档草稿。
- AI 不得生成或修改 `backend/app/human_only/` 内的核心算法实现。
- 所有 AI 生成代码必须经过人工阅读、运行验证后才允许提交。
- 涉及权限、薪资、候选人评分、面试排期、RAG 来源展示的 AI 生成代码，必须由对应模块负责人复核。

## AI 禁飞区规范

禁飞区只包含以下三项人工手写核心算法：

- `backend/app/human_only/resume_scoring.py`
  - 职责：简历多维加权评分。
  - 唯一公开函数：`score_resume(...)`。
  - 独立测试文件：`backend/tests/human_only/test_resume_scoring.py`。
- `backend/app/human_only/interview_scheduler.py`
  - 职责：面试排期约束满足。
  - 唯一公开函数：`schedule_interview(...)`。
  - 独立测试文件：`backend/tests/human_only/test_interview_scheduler.py`。
- `backend/app/human_only/salary_access_control.py`
  - 职责：薪资查询权限校验。
  - 唯一公开函数：`check_salary_access(...)`。
  - 独立测试文件：`backend/tests/human_only/test_salary_access_control.py`。

禁飞区限制：

- 每项禁飞区只保留一个主实现文件。
- 每个主实现文件对外只暴露一个公共入口函数。
- 禁止直接依赖 FastAPI、SQLAlchemy、LangGraph、ChromaDB、HTTP 请求、数据库连接或大模型接口。
- 只接收结构化输入，只输出结构化结果。
- 修改禁飞区时必须写明关联 Issue，并同步更新 `.agent/decisions.md` 中的相关决策记录。

## 测试规范

- 禁飞区优先编写独立单元测试。
- 出现候选人评分、面试排期或薪资权限相关 Bug 时，先运行对应 `human_only` 测试。
- 对应 `human_only` 测试通过后，再继续排查 Service、API、Agent Tool、数据库或前端。
- 非禁飞区功能测试按风险决定范围，优先覆盖权限、状态流转、Agent 工具调用和 RAG 来源展示。

## 配置规范

- 真实 API Key、密码、Token 不得提交到仓库。
- 只提交 `.env.example`。
- 本地开发、演示和部署所需配置通过环境变量或 Docker Compose 注入。

## 命名规范

- Python 文件、变量和函数使用 `snake_case`。
- Vue 组件使用 `PascalCase`。
- TypeScript 变量和函数使用 `camelCase`。
- 业务模块命名应与后端模块边界保持一致。

## 文档规范

- 关键技术决策同步更新 `.agent/decisions.md`。
- 架构变化同步更新 `.agent/architecture.md`。
- 文档不得虚构已完成的代码、数据库表、接口或测试结果。
