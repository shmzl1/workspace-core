# TalentFlow 协作规范

## 分支策略

- 只使用 `dev` 和 `main`。
- `dev` 是开发主线。
- `main` 是稳定分支。
- 禁止直接向 `main` 提交。

## Commit 规范

- Commit 类型只使用 `feat`、`fix`、`docs`、`refactor`。
- 提交需关联 Issue 或任务说明。
- 不使用无法说明目的的提交信息。

## 架构规范

- 项目只维护一套 FastAPI 后端。
- Vue Web 管理端、微信小程序员工端和 Gradio 内部调试台共享后端 API 与 Service。
- 普通业务遵循 `API -> Service -> Repository -> PostgreSQL`。
- Agent 遵循 `Agent -> Tool -> Service -> human_only`。
- 后端采用模块化单体，不使用微服务，不新增第二套后端。

## 模块命名约定

- 后端业务模块放入 `backend/app/modules/`。
- 共享能力放入 `backend/app/shared/`。
- Agent 编排放入 `backend/app/agents/`。
- RAG 能力放入 `backend/app/rag/`。
- 前端共享组件放入 `frontend/src/shared/`。
- 招聘功能放入 `frontend/src/features/recruitment/`。
- 员工端 Web 功能放入 `frontend/src/features/employee/`。

## AI 禁飞区

AI 不得创建、修改、移动、删除、格式化或补全：

- `backend/app/human_only/resume_scoring.py`
- `backend/app/human_only/interview_scheduler.py`
- `backend/app/human_only/salary_access_control.py`
- `backend/tests/human_only/test_resume_scoring.py`
- `backend/tests/human_only/test_interview_scheduler.py`
- `backend/tests/human_only/test_salary_access_control.py`

禁飞区保持纯 Python，不依赖 FastAPI、SQLAlchemy、LangGraph、ChromaDB、HTTP 客户端、数据库连接或 LLM。

## 命令执行规范

- 默认不执行 Conda、pip、npm、Docker、Git、测试、构建、迁移或启动命令。
- 如确需执行，必须由任务明确要求。

## 配置与数据规范

- 不创建真实 `.env`。
- 不提交真实 API Key、Token、密码、JWT 密钥和数据库凭据。
- 不提交真实企业数据、本地 Chroma 数据、真实上传文件或真实报告。

## 文档同步

- 架构变化更新 `.agent/architecture.md` 和 `docs/架构设计.md`。
- 决策变化更新 `.agent/decisions.md`。
- 需求、接口、数据模型、考勤、薪资预审和权限变化同步更新 docs。
