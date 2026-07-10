# 招聘专业 Service 边界

当前可运行链路由 `RecruitmentRunContextService` 校验岗位、候选人和投递关系，再把脱离数据库 Session 的上下文交给进程内 Runtime。

后续专业链路约定为 `Agent -> Tool -> 专业 Service -> 现有 RecruitmentService / Repository / human_only`。Agent 和 Tool 不得直接访问 Repository 或 `human_only`。

`contracts.py` 只定义候选人评估、招聘要求和报告汇总 Protocol，不代表这些专业 Service 已实现。现有 `RecruitmentService` 及其业务行为保持不变。
