# docs 文档约束

## 覆盖范围

本文件约束 `docs/` 下所有项目文档。

## 写作规则

- 使用中文 Markdown。
- 使用“规划中”“待 Sprint 实现”“架构约定”“当前仅有脚手架/空目录”等真实状态表述。
- 不得声称未验证功能已经运行、部署、测试通过或接口已验证。
- 不写空泛宣传语，不虚构性能数据、接口返回、截图、测试通过率、部署结果或账号密码。
- 术语保持一致：招聘策略 Agent、简历解析 Agent、岗位匹配 Agent、面试评估 Agent、决策审查 Agent、HR 最终报告、员工服务 Agent、薪资预审助手、AI 禁飞区。
- 明确人工禁飞区与 AI 可生成工程代码的边界。
- 明确 Agent 只解释建议，HR 才能确认工资。
- 分支只写 `dev` 和 `main`，不描述其他分支工作流。
- 分支描述必须写明：`dev` 是开发主线，`main` 是稳定版本分支，禁止直接向 `main` 提交，不写 `feature/*` 流程。
- 架构描述必须保持：一套 FastAPI 后端，Vue Web 管理端、微信小程序员工端、Gradio 内部调试台共享同一套 FastAPI 后端；模块化单体，不新增第二套后端。
- 调用链统一写为：普通业务请求 `API -> Service -> Repository -> PostgreSQL`；普通业务调用核心算法 `API -> Service -> human_only`；Agent 任务调用核心算法 `Agent -> Tool -> Service -> human_only`；RAG 问答 `Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 禁飞区文件和核心测试不得被描述为 AI 可生成内容。
- AI 禁飞区核心实现只包含 `backend/app/human_only/resume_scoring.py`、`backend/app/human_only/interview_scheduler.py`、`backend/app/human_only/salary_access_control.py`。
- AI 禁飞区核心测试只包含 `backend/tests/human_only/test_resume_scoring.py`、`backend/tests/human_only/test_interview_scheduler.py`、`backend/tests/human_only/test_salary_access_control.py`。
- Agent 文档必须说明 Agent 不访问 Repository，Tool 只能调用 Service。
- `AGENT_THINKING` 只能描述可审计结构化阶段摘要，不得描述为隐藏思维链。
- 前端事件文档不得使用随机日志、固定延迟或静态事件冒充真实 Agent 执行。
- 目录重构采用兼容迁移，未确认 import 迁移和测试前不得建议删除旧路径。

## 更新规则

- 需求变化更新 `需求说明.md`。
- 架构变化更新 `架构设计.md`。
- 数据模型变化更新 `数据库设计.md`。
- API 契约变化更新 `接口契约.md`。
- Agent、RAG、Tool 边界变化更新 `Agent设计.md`。
- 考勤、薪资预审或权限变化更新 `考勤与薪资预审规则.md`。
- AI 使用边界变化更新 `AI使用与禁飞区说明.md`。
