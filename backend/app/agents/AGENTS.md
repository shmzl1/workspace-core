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
- 不得绕过权限、不得直接查询数据库、不得直接调用禁飞区内部实现。

## 薪资预审限制

- Agent 只能解释、总结、提示异常和给出审查建议。
- Agent 不得确认工资、修改工资、删除扣款或写入已确认薪资。
- HR 才能执行最终确认动作。

## Trace 要求

- Agent 调用应保留输入摘要、工具调用、RAG 来源、关键中间结果、错误信息和 `trace_id`。
