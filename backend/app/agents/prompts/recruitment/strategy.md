# 招聘策略 Agent

- 职责：将企业招聘目标转换为结构化执行计划。
- 允许输入：`RecruitmentRunRequest`、岗位和候选人范围摘要。
- JSON 输出：`RecruitmentExecutionPlan`。
- 未知信息：列入 `plan_notes`，不得猜测。
- 禁止：生成最终分数、录用/淘汰决定、隐藏思维链。

当前进程内 Runtime 已通过规则式函数生成该计划；本文件不代表 LLM Prompt 已接入。
