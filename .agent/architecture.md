# TalentFlow 架构说明

## 总体架构

TalentFlow 智聘中枢采用 Vue Web 管理端、微信小程序员工端、Gradio 内部调试台和一套 FastAPI 后端。后端采用模块化单体，统一连接 PostgreSQL、ChromaDB RAG、LangGraph Agent 和 AI 禁飞区。

## 固定约束

- 一套 FastAPI 后端。
- Vue Web 管理端、微信小程序员工端、Gradio 内部调试台共享同一套 FastAPI 后端。
- 普通业务请求：`API -> Service -> Repository -> PostgreSQL`。
- 普通业务调用核心算法：`API -> Service -> human_only`。
- Agent 任务调用核心算法：`Agent -> Tool -> Service -> human_only`。
- RAG 问答：`Agent/Tool -> RAG -> ChromaDB -> LLM -> 带来源回答`。
- 模块化单体，不使用微服务。
- 不新增第二套后端。
- 不引入 Redis、Celery、RabbitMQ、Kubernetes，除非后续团队明确重新决策并更新 `.agent/decisions.md`。
- Route/API 不直接访问数据库，不直接调用 `human_only`。
- Agent 不直接访问 Repository，不直接调用 `human_only`。
- 前端、小程序、Gradio 不直接访问数据库、禁飞区或底层算法。

## 架构图

```mermaid
flowchart TB
    Web[Vue Web 管理端]
    Mini[微信小程序员工端]
    Gradio[Gradio 内部调试台]
    API[一套 FastAPI 后端]
    Service[业务 Service]
    Repo[Repository]
    PG[(PostgreSQL)]
    Agent[LangGraph Agent]
    Tool[LangChain Tools]
    RAG[ChromaDB RAG]
    Human[AI 禁飞区]

    Web --> API
    Mini --> API
    Gradio --> API
    API --> Service
    Service --> Repo
    Repo --> PG
    API --> Agent
    Agent --> Tool
    Tool --> Service
    Tool --> RAG
    RAG --> LLM[LLM]
    Service --> Human
```

## AI 禁飞区边界

AI 禁飞区核心实现文件只包含：

- `backend/app/human_only/resume_scoring.py`
- `backend/app/human_only/interview_scheduler.py`
- `backend/app/human_only/salary_access_control.py`

对应核心测试只包含：

- `backend/tests/human_only/test_resume_scoring.py`
- `backend/tests/human_only/test_interview_scheduler.py`
- `backend/tests/human_only/test_salary_access_control.py`

AI 不得创建、修改、移动、删除、格式化、补全上述文件，不得复制、重写、模拟、绕过禁飞区核心算法。禁飞区只能由人工负责人维护，保持纯 Python，不依赖 FastAPI、SQLAlchemy、LangGraph、ChromaDB、HTTP 客户端、数据库连接或 LLM。

`human_only` 内部公开函数统一为 `score_resume(...)`、`schedule_interview(...)`、`check_salary_access(...)`。Service 层可以包装为 `score_candidates(...)`、`generate_schedule(...)`、`check_salary_access(...)`。Agent Tool 只能调用 Service 层函数。

## Web、员工端、小程序边界

- Web 管理端：招聘、候选人、排期、薪资预审、审计、驾驶舱和员工服务。
- Web 员工侧：考勤、年假、本人薪资、制度查询和员工服务 Agent。
- 小程序：仅员工端简单功能，包括首页、签到、签退、今日考勤、本月考勤、年假余额、本人薪资摘要和制度查询。
- 小程序不接 HR 招聘、排期、薪资预审和审计后台。

## 考勤到薪资预审数据流

1. 员工签到或签退。
2. 后端记录考勤事实和状态。
3. HR 查看月度考勤汇总。
4. 薪资预审读取考勤事实和月度汇总。
5. 规则引擎生成预审明细。
6. AI 解释异常和提供审查建议。
7. HR 执行最终确认。

## 薪资预审与确认分离

- 规则引擎负责计算。
- AI 负责解释和建议。
- HR 负责确认。
- Agent 不得确认工资、修改工资、删除扣款或写入已确认薪资。

## Gradio 定位

Gradio 仅用于内部 Agent 调试，查看 LangGraph 执行链、工具调用、RAG 命中、错误信息和 Trace。

## 数据库模型基线

- SQLAlchemy 基线入口：`backend/app/core/database.py`。
- 模型注册入口：`backend/app/modules/model_registry.py`。
- 业务模型位置：`backend/app/modules/*/models.py`。
- 首次迁移：`backend/alembic/versions/0001_initial_schema.py`，迁移编号 `0001_initial_schema`。
- 当前迁移只建立表结构、外键、唯一约束、检查约束和索引，不写入种子数据。
- 本次未执行 `alembic upgrade head`，实际数据库升级由人工在本地环境确认后执行。

## Sprint 1 平台代码状态

- FastAPI 使用 JWT 确认身份，并在每次请求从数据库读取账号状态、角色、权限和关联员工档案；业务授权依据为 `users.permissions`。
- 招聘、面试、员工、考勤、薪资和审计已建立基础 Route -> Service -> Repository 只读链路。
- 演示种子数据放在 `data/seed/`，导入入口为 `scripts/build-demo-data.py` 和 `scripts/seed-data.ps1`。
- 薪资访问只通过 `PayrollAccessService` 调用人工禁飞区公开函数；禁飞区文件未提供时拒绝访问，不模拟核心算法。
