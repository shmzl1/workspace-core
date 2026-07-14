# Agent Runtime

本目录保存 Agent Run 契约、招聘 Runner 与 SSE 分发代码。PostgreSQL 持久化实现位于 `app/modules/agent_runtime/`，代码存在，待本地人工验收。

- `run_store.py`：Store Protocol、旧测试兼容内存 Store 和容器管理的 PostgreSQL Store 兼容入口。
- SSE Subscriber Queue 只保存在当前进程；历史 Run、节点、事件和 Tool 调用从 PostgreSQL 恢复。
- `recruitment_runner.py`：当前执行招聘策略、企业知识检索、确定性简历解析、岗位匹配、规则式决策审查与 HR 最终报告；无真实结构化面试评价时仅面试评估节点保持 `SKIPPED`。招聘策略叙述增强与知识检索并行执行，模型增强超过独立预算时回退到确定性结果。相关代码存在，待本地人工验收。
- `event_stream.py`：重放历史 `AgentEvent`、订阅新增事件并发送心跳。

Runtime 只负责 Run 生命周期、工作流编排、事件与流式传输，不访问 Repository，不调用 `human_only`；当前不使用 LangGraph。LLM 与 RAG 均为可关闭、可降级的增强能力，相关代码存在，待本地人工验收。
