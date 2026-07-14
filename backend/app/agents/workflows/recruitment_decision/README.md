# 招聘多 Agent 工作流

正式链路为：企业招聘目标 → 招聘策略 Agent → 简历解析 Agent / 岗位匹配 Agent / 面试评估 Agent → 决策审查 Agent → HR 最终报告 → HR 人工决定。

PostgreSQL Runtime、确定性工作流、招聘策略与 HR 报告的可选 LLM 增强、ChromaDB 企业知识、简历解析、岗位匹配和决策审查代码存在，待本地人工验收。`graph.py` 继续只保存静态节点与依赖元数据；当前不使用 LangGraph。面试评价无真实结构化反馈时仍明确标记为 `SKIPPED`。

招聘策略叙述增强与企业知识检索并行执行；招聘策略和 HR 报告模型增强均关闭深度思考、限制输出长度并受独立节点内预算约束。模型超时不阻断工作流，确定性计划或报告继续输出并标记 `RULE_BASED_FALLBACK`。相关代码存在，待本地人工验收。

岗位匹配依赖简历解析；面试评估必须使用真实面试数据。Agent 不访问 Repository 或 `human_only`，未来只能通过 Tool 调用 Service。录用、淘汰、排期确认和薪资确认均由人工完成。
