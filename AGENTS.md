# TalentFlow 根级协作约束

## 项目边界

- TalentFlow 智聘中枢是面向招聘决策、员工服务、考勤薪资预审与权限审计的可解释企业人力资源管理 Agent。
- 项目采用一套 FastAPI 后端，Vue Web 管理端、微信小程序员工端和 Gradio 内部调试台共享同一套后端与业务 Service。
- 后端保持模块化单体，不采用微服务，不新增第二套后端。
- Gradio 仅用于内部 Agent 调试，不作为正式业务入口。

## 分层调用

- 普通业务：`API -> Service -> Repository -> PostgreSQL`。
- Agent 任务：`Agent -> Tool -> Service -> human_only`。
- RAG 问答：`Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 前端、小程序和 Gradio 不得直接访问数据库、禁飞区或底层算法。

## 分支与提交

- 只使用 `dev` 和 `main`。
- `main` 为稳定分支，`dev` 为开发主线。
- 禁止直接向 `main` 提交。
- Commit 类型只使用 `feat`、`fix`、`docs`、`refactor`，并关联 Issue 或任务说明。

## AI 禁飞区

AI 不得创建、修改、移动、删除、格式化或补全以下文件：

- `backend/app/human_only/resume_scoring.py`
- `backend/app/human_only/interview_scheduler.py`
- `backend/app/human_only/salary_access_control.py`
- `backend/tests/human_only/test_resume_scoring.py`
- `backend/tests/human_only/test_interview_scheduler.py`
- `backend/tests/human_only/test_salary_access_control.py`

禁飞区算法只能由人工负责人实现。工程代码只能通过既有公开函数调用禁飞区，不得复制、绕过或模拟核心算法。

## 默认执行规则

- 默认不运行 Conda、pip、npm、Docker、Git、测试、构建、迁移或启动命令。
- 不创建真实 `.env` 文件。
- 不写入真实 API Key、Token、密码、数据库凭据或 JWT 密钥。
- 不提交真实上传文件、本地 Chroma 数据、真实报告和真实企业数据。

## 文档同步

- 架构变化同步更新 `.agent/architecture.md` 和 `docs/架构设计.md`。
- 规则、权限、薪资预审、考勤边界变化同步更新相关 docs。
- 技术决策变化同步更新 `.agent/decisions.md`。
