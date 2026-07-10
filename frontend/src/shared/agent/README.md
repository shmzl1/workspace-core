# 前端 Agent 公共契约

`contracts.ts` 是前端唯一的 Agent Enum 与数据类型来源，字段与后端保持 `snake_case`。业务 feature 只能重导出，不复制类型定义。

`AGENT_THINKING` 表示“可审计的结构化阶段摘要”，不表示模型隐藏思维链。当前 Agent API、SSE 客户端和招聘评估页面代码存在，待本地人工验收。
