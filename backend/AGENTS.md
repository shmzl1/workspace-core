# backend 后端约束

## 覆盖范围

本文件约束 `backend/` 下除 `backend/app/human_only/` 与 `backend/tests/human_only/` 禁飞区文件外的后端工程。

## 架构规则

- 仅维护一套 FastAPI 后端。
- Vue Web 管理端、微信小程序员工端和 Gradio 内部调试台共享同一套 FastAPI 后端 API 与业务 Service。
- 普通业务请求：`API -> Service -> Repository -> PostgreSQL`。
- 普通业务调用核心算法：`API -> Service -> human_only`。
- Agent 任务调用核心算法：`Agent -> Tool -> Service -> human_only`。
- RAG 问答：`Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 不新增微服务，不新增第二套后端，不引入 Redis、Celery、RabbitMQ、Kubernetes，除非后续团队明确重新决策并更新 `.agent/decisions.md`。

## 模块边界

- FastAPI 是唯一后端入口，`app/main.py` 是应用入口。
- Route 不直接访问数据库。
- Route 不直接调用 `human_only`。
- Agent 不直接访问 Repository。
- Agent 不直接调用 `human_only`。
- `api/` 只负责路由聚合、请求校验、响应封装和调用 Service。
- `modules/` 保存业务模块，每个模块内部再按模型、Schema、Repository、Service 分层。
- Service 负责编排业务流程、权限和审计。
- Repository 只负责数据库读写。
- 跨模块调用优先调用目标模块 Service，不跨层访问目标模块 Repository。
- `agents/` 保存 LangGraph 编排、工具、提示词和 Trace。
- `rag/` 保存 ChromaDB 检索、导入和来源组织。
- `shared/` 保存通用响应、分页、Trace、常量和文件存储等跨模块能力。
- `agent_console/` 只服务 Gradio 内部调试。
- 模型变更时同步 `docs/数据库设计.md` 和 `data/seed/README.md`。
- 错误响应必须保留 `trace_id`。
- 权限判断只以服务端结果为准。

## 禁止事项

- 不在 API 层直接访问数据库。
- 不让 Agent 直接访问 Repository 或禁飞区。
- 不在普通业务模块复制禁飞区算法。
- 不自动执行数据库迁移、Docker 启动、服务启动或构建命令。
- 数据库迁移 `alembic upgrade head` 必须由人工确认后执行。
- 不创建真实 `.env`，不提交真实密钥或真实数据。
