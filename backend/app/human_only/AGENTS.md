# backend/app/human_only AI 禁飞区约束

## 覆盖范围

本文件约束 `backend/app/human_only/`。

## 禁飞区文件

以下三个文件只能由人工负责人创建和维护：

- `resume_scoring.py`
- `interview_scheduler.py`
- `salary_access_control.py`

## 人工负责人

- 黄钧：`resume_scoring.py`、`interview_scheduler.py`
- 吴越：`salary_access_control.py`

## 严格禁止

- AI 不得创建、修改、移动、删除、格式化或补全上述文件。
- AI 不得复制、重写、替代、绕过或模拟禁飞区核心算法。
- 禁飞区不得依赖 FastAPI、SQLAlchemy、LangGraph、ChromaDB、HTTP 客户端、数据库连接或 LLM。

## 允许的调用边界

普通工程代码只能通过 Service 层既有公开函数调用：

- `score_candidates(...)`
- `generate_schedule(...)`
- `check_salary_access(...)`

Agent 调用链必须是 `Agent -> Tool -> Service -> human_only`。Route 不得直接调用本目录文件。
