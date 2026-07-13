# Agent Runtime

本目录保存 Agent Run 契约、招聘 Runner 与 SSE 分发代码。PostgreSQL 持久化实现位于 `app/modules/agent_runtime/`，代码存在，待本地人工验收。

- `run_store.py`：Store Protocol、旧测试兼容内存 Store 和容器管理的 PostgreSQL Store 兼容入口。
- SSE Subscriber Queue 只保存在当前进程；历史 Run、节点、事件和 Tool 调用从 PostgreSQL 恢复。
- `recruitment_runner.py`：当前执行规则式招聘策略、企业知识本地回退与确定性简历解析；岗位匹配及后续四个节点保持 `SKIPPED`。
- `event_stream.py`：重放历史 `AgentEvent`、订阅新增事件并发送心跳。

Runtime 只负责 Run、事件与流式传输，不访问 Repository，不调用 `human_only`，也不代表 LangGraph、LLM 或真实 RAG 已接入。
