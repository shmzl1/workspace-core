# backend/app/agents Agent 约束

## 覆盖范围

本文件约束 LangGraph Agent、Tools、Prompts、Trace 与 Guardrails。

## Agent 类型

- 员工服务 Agent：查询年假、制度、本人薪资摘要和员工服务信息。
- 招聘决策 Agent：辅助岗位、候选人、评分解释、排期建议和招聘报告。
- 薪资预审助手：解释薪资预审结果、提示异常和生成审查建议。

## 调用规则

- Agent 只能通过 Tool 调用业务能力。
- Tool 只能通过 Service 使用业务模块。
- 需要核心算法时必须走 `Tool -> Service -> human_only`。
- RAG 问答必须走 `Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 不得绕过权限、不得直接查询数据库、不得直接访问 Repository、不得直接调用禁飞区内部实现。
- 员工服务 Agent 只能查询本人授权数据。
- 招聘决策 Agent 不得绕过评分 Service 和排期 Service。
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

## 架构边界

- Agent 共享同一套 FastAPI 后端与业务 Service，不新增第二套后端。
- 不引入 Redis、Celery、RabbitMQ、Kubernetes，除非后续团队明确重新决策并更新 `.agent/decisions.md`。
- 默认不运行 Conda、pip、npm、Docker、Git、数据库迁移、启动服务或构建命令。
