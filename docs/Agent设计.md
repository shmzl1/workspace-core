# Agent 设计

本文记录 Agent 边界与当前实现状态。Sprint 2.1 已真实运行招聘策略 Agent；不表示其他 Agent、LangGraph、LLM 或 RAG 已完成。

## Sprint 2.1 招聘策略运行

```text
HR 提交真实岗位、候选人与企业招聘目标
→ RecruitmentRunContextService 校验投递关系
→ 创建进程内 Run 和真实 run_id
→ 招聘策略 Agent 生成 RecruitmentExecutionPlan
→ SSE 发布真实 AgentEvent
→ 前端增量更新工作流与执行计划
```

策略计划完全由已校验请求、真实岗位摘要、候选人 ID 和静态 Graph 元数据生成，不访问数据库、不调用 Tool、LLM 或 RAG。真实事件顺序为：

1. `WORKFLOW_STARTED`
2. `AGENT_STARTED`
3. `AGENT_THINKING`
4. `PLAN_CREATED`
5. `AGENT_COMPLETED`
6. `WORKFLOW_COMPLETED`

运行完成时招聘策略 Agent 为 `COMPLETED`，简历解析、岗位匹配、面试评估、决策审查和 HR 最终报告为 `SKIPPED`，原因统一为 `CURRENT_PHASE_NOT_IMPLEMENTED`。Run 仅保存在当前后端进程中，重启后不可恢复。

`AGENT_THINKING` 只包含当前目标、候选人数、当前动作、缺失信息和下一步计划等可审计结构化摘要，不包含模型隐藏思维链。

## 员工服务 Agent

- 输入：员工自然语言问题、当前员工身份、角色上下文。
- 可调用 Tool：年假查询、本人薪资摘要查询、考勤摘要查询、制度 RAG 查询。
- 不可调用 Tool：HR 薪资预审、候选人管理、招聘排期、审计后台写操作。
- 输出：回答、制度来源、权限说明、工具调用摘要。
- Trace：保留问题、工具调用、权限判断、RAG 来源和错误信息。
- RAG 来源：制度问答必须返回命中的制度文档和片段。
- 降级策略：无模型 Key 时返回普通业务查询结果或提示待 Agent 接入。

## 招聘多 Agent 工作流

- 当前已实现：招聘策略 Agent 规则式执行计划。
- 后续节点：简历解析 Agent、岗位匹配 Agent、面试评估 Agent、决策审查 Agent、HR 最终报告。
- 输入：企业招聘目标、真实岗位、真实候选人投递和 HR 操作上下文。
- 可调用 Tool：岗位 Service、候选人 Service、评分 Service、排期 Service、报告 Service。
- 不可调用 Tool：薪资确认、薪资修改、无权限薪资查询、禁飞区内部函数。
- 当前输出：`RecruitmentExecutionPlan`、真实 Run Snapshot 和 AgentEvent。
- Trace：保留候选人筛选条件、评分调用、排期调用和解释摘要。
- RAG 来源：涉及制度或招聘规则时返回来源。
- 降级策略：核心算法未接入时不模拟算法结果，只提示待人工禁飞区接入。

## 薪资预审助手

- 输入：薪资预审记录、扣款明细、考勤摘要、HR 问题。
- 可调用 Tool：薪资预审查询、考勤来源查询、规则来源查询、审计记录查询。
- 不可调用 Tool：确认工资、修改工资、删除扣款、写入已确认薪资。
- 输出：异常解释、扣款来源说明、审查建议。
- Trace：保留薪资记录、权限判断、规则来源和输出摘要。
- RAG 来源：涉及制度解释时返回制度来源。
- 降级策略：无模型 Key 时展示规则计算过程和人工审查提示。
## 数据访问边界

- Agent 不直接访问 SQLAlchemy Session、ORM Model 或数据库连接。
- Agent 任务遵循 `Agent -> Tool -> Service -> Repository / human_only`。
- 制度问答遵循 `Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 候选人评分、面试排期和薪资权限只能通过 Service 调用禁飞区公开函数，不能绕过禁飞区边界。
