# AI 使用与禁飞区说明

## AI 禁飞区文件

- `backend/app/human_only/resume_scoring.py`
- `backend/app/human_only/interview_scheduler.py`
- `backend/app/human_only/salary_access_control.py`

## 人工负责人

- 黄钧：`resume_scoring.py`、`interview_scheduler.py`
- 吴越：`salary_access_control.py`

## 核心测试禁飞区

- `backend/tests/human_only/test_resume_scoring.py`
- `backend/tests/human_only/test_interview_scheduler.py`
- `backend/tests/human_only/test_salary_acc`AI 允许生成范围
- Vue Web 前端。
- 微信小程序页面。
- FastAPI 路由。
- SQLAlchemy 模型。
- Pydantic Schema。
- Repository、Service。
- LangGraph Agent、Tool、RAG、Gradio 调试台。
- 普通测试。
- Docker Compose、Nginx、环Agent 调用链

```text
Agent -> Tool -> Service -> human_only
```

禁止 Agent、Tool、前端或小程序直接调用禁飞区内部实现。
禁止复制、模拟、绕过禁飞区算法；Route 不得直接调用 `human_only`。

## 人工负责人需要解释的内容

- 模块需求。
- Prompt 和 AI 生成代码审查结果。
- 数据流、关键逻辑和接口关系。
- 禁飞区算法输入、输出和边界。

## AI 使用反思文档位置

AI 使用反思文档放在 `docs/ai-usage/`。
