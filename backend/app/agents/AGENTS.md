# backend/app/agents Agent 约束

## 覆盖范围

本文件约束持久化 Runtime、Agent 契约、未来 LangGraph 编排、Tools、Prompts、Trace 与 Guardrails。

## 正式 Agent 类型

- 招聘主工作流：企业招聘目标 → 招聘策略 Agent → 简历解析 Agent / 岗位匹配 Agent / 面试评估 Agent → 决策审查 Agent → HR 最终报告 → HR 人工决定。
- 员工服务 Agent：独立查询本人考勤、年假、制度和本人薪资摘要。
- 薪资预审助手：独立解释薪资预审结果、提示异常和生成审查建议。

## 目录职责

- `runtime/`：Store 契约、Runner 与 SSE；PostgreSQL Store 实现在业务模块中，当前进程只保存 SSE Subscriber Queue。
- `shared/`：公共 Enum、Pydantic、Protocol、State、Event、Trace 与 Guardrail。
- `workflows/`：领域契约和静态节点元数据，不创建假可执行 Graph。
- `tools/`：ToolContract 与兼容入口；新 Agent 代码只通过 Service 工作。
- `prompts/`：职责与输出 Schema 边界，不代表模型已接入。
- 一个业务工作流一个目录；招聘工作流的每个顶层 Agent 当前对应一个 Python 文件，只有出现多个内部节点、Schema、测试和大量逻辑时再拆子目录。

## 调用规则

- Agent 只能通过 Tool 调用业务能力。
- Tool 只能通过 Service 使用业务模块。
- 需要核心算法时必须走 `Tool -> Service -> human_only`。
- RAG 问答必须走 `Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 不得绕过权限、不得直接查询数据库、不得直接访问 Repository、不得直接调用禁飞区内部实现。
- 员工服务 Agent 只能查询本人授权数据。
- 招聘 Agent 不得绕过评分 Service 和排期 Service，不自动录用或淘汰。
- 面试评估 Agent 无真实数据时只能标记待面试，不得伪造评价或确认排期。
- Agent Tool 只能调用 Service 层函数，不能直接调用 `score_resume(...)`、`schedule_interview(...)`、`check_salary_access(...)` 等 `human_only` 函数。
- AI 不得复制、重写、模拟、绕过禁飞区核心算法。

## 薪资预审限制

- Agent 只能解释、总结、提示异常和给出审查建议。
- Agent 不得确认工资、修改工资、删除扣款或写入已确认薪资。
- HR 才能执行最终确认动作。
- LLM 故障不得影响评分、排期、考勤、薪资预审和权限等确定性功能。
- RAG 回答必须带来源。

## Trace 要求

- Agent 调用应保留输入摘要、工具调用、RAG 来源、关键中间结果、错误信息和 `trace_id`。
- `AGENT_THINKING` 只表示可审计的结构化阶段摘要，不得记录或展示隐藏思维链。
- 不记录 API Key、JWT、密码、数据库连接串、完整简历、完整联系方式或完整薪资。
- 前端不得伪造 Agent 日志、随机事件或固定延迟。

## 架构边界

- Agent 共享同一套 FastAPI 后端与业务 Service，不新增第二套后端。
- 不引入 Redis、Celery、RabbitMQ、Kubernetes，除非后续团队明确重新决策并更新 `.agent/decisions.md`。
- 默认不运行 Conda、pip、npm、Docker、Git、数据库迁移、启动服务或构建命令。
- 目录重构保留旧 import 兼容入口；未完成依赖迁移和测试前不删除旧文件。
- 当前状态只写“代码存在，待本地人工验收”“已建立目录或契约”“计划中”。
