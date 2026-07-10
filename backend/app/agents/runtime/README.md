# Agent Runtime

本目录保存当前进程内 Agent Run 生命周期、事件存储、招聘策略 Runner 与 SSE 分发代码。代码存在，待本地人工验收。

- `run_store.py`：有界进程内 Run 与事件存储；不是持久化任务系统，后端重启后记录丢失。
- `recruitment_runner.py`：当前只执行规则式招聘策略计划，其余五个招聘节点保持 `SKIPPED`。
- `event_stream.py`：重放历史 `AgentEvent`、订阅新增事件并发送心跳。

Runtime 只负责 Run、事件与流式传输，不访问 Repository，不调用 `human_only`，也不代表 LangGraph、LLM 或真实 RAG 已接入。
