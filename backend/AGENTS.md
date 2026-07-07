# backend 后端约束

## 覆盖范围

本文件约束 `backend/` 下除 `backend/app/human_only/` 与 `backend/tests/human_only/` 禁飞区文件外的后端工程。

## 架构规则

- 仅维护一套 FastAPI 后端。
- Web 管理端、微信小程序员工端和 Gradio 内部调试台共享后端 API 与业务 Service。
- 普通业务调用链为 `API -> Service -> Repository -> PostgreSQL`。
- Agent 调用链为 `Agent -> Tool -> Service -> human_only`。
- 不新增微服务，不新增第二套后端，不引入 Redis、Celery、RabbitMQ、Kubernetes。

## 模块边界

- `api/` 只负责路由聚合、请求校验、响应封装和调用 Service。
- `modules/` 保存业务模块，每个模块内部再按模型、Schema、Repository、Service 分层。
- `agents/` 保存 LangGraph 编排、工具、提示词和 Trace。
- `rag/` 保存 ChromaDB 检索、导入和来源组织。
- `shared/` 保存通用响应、分页、Trace、常量和文件存储等跨模块能力。
- `agent_console/` 只服务 Gradio 内部调试。

## 禁止事项

- 不在 API 层直接访问数据库。
- 不让 Agent 直接访问 Repository 或禁飞区。
- 不在普通业务模块复制禁飞区算法。
- 不创建真实 `.env`，不提交真实密钥或真实数据。
