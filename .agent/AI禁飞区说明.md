# backend/app/human_only AI 禁飞区约束

## 覆盖范围

本文件约束 `backend/app/human_only/`。

## 禁飞区文件

AI 禁飞区核心实现文件只包含以下三个文件，并且只能由人工负责人创建和维护：

- `backend/app/human_only/resume_scoring.py`
- `backend/app/human_only/interview_scheduler.py`
- `backend/app/human_only/salary_access_control.py`

## 人工负责人

- 黄钧：`resume_scoring.py`、`interview_scheduler.py`
- 吴越：`salary_access_control.py`

## 严格禁止

- AI 不得创建、修改、移动、删除、格式化或补全上述文件。
- AI 不得复制、重写、替代、绕过或模拟禁飞区核心算法。
- 禁飞区不得依赖 FastAPI、SQLAlchemy、LangGraph、ChromaDB、HTTP 客户端、数据库连接或 LLM。
- 禁飞区只接收结构化输入，只输出结构化结果。

## 允许的调用边界

`human_only` 内部公开函数统一为：

- `score_resume(...)`
- `schedule_interview(...)`
- `check_salary_access(...)`

Service 层可以包装为：

- `score_candidates(...)`
- `generate_schedule(...)`
- `check_salary_access(...)`

普通业务调用核心算法必须是 `API -> Service -> human_only`。Agent 调用核心算法必须是 `Agent -> Tool -> Service -> human_only`。Route/API 和 Agent Tool 都不得直接调用本目录文件。
