# 招聘多 Agent 工作流

正式链路为：企业招聘目标 → 招聘策略 Agent → 简历解析 Agent / 岗位匹配 Agent / 面试评估 Agent → 决策审查 Agent → HR 最终报告 → HR 人工决定。

当前进程内 Runtime 调用规则式 `build_recruitment_execution_plan(...)`、企业知识本地混合回退 Service 和确定性简历解析 Service 的代码存在，待本地人工验收：招聘策略与简历解析节点执行，岗位匹配、面试评价、决策审查和报告节点标记为 `SKIPPED`。`graph.py` 仅保存静态节点与依赖元数据；没有 LangGraph、LLM、ChromaDB、专业评分、面试评价、审查或报告生成执行。

岗位匹配依赖简历解析；面试评估必须使用真实面试数据。Agent 不访问 Repository 或 `human_only`，未来只能通过 Tool 调用 Service。录用、淘汰、排期确认和薪资确认均由人工完成。
