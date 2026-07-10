# Agent 公共层

本目录提供状态、事件、Trace、Guardrail、来源引用和模型网关契约，不编排工作流、不调用模型、不访问数据库。

- `contracts.py`：运行时枚举、事件、Snapshot、来源和 Tool 契约。
- `state.py`：与 LangGraph 解耦的通用状态；`actor_user_id` 保持必填。
- `events.py`：由当前进程内 RunStore 实现的事件发布/订阅接口。
- `trace.py`：结构化摘要脱敏边界。
- `guardrails.py`：仅约束 Agent Runtime 与 Agent 节点的导入，不限制正常 API 通过依赖获取数据库 Session。
- `model_gateway.py`：未来模型网关输入输出 Protocol，不读取密钥、不发 HTTP 请求。

SSE 实现代码位于 `agents/runtime/`，当前状态为“代码存在，待本地人工验收”；`AGENT_THINKING` 仅表示可审计结构化阶段摘要，不是隐藏思维链。
