# TalentFlow 智聘中枢

TalentFlow 智聘中枢是面向招聘决策、员工服务、考勤薪资预审与权限审计的可解释企业人力资源管理 Agent。

## 当前状态

当前状态：PostgreSQL Agent Run 持久化、OpenAI-compatible 模型增强、Embedding、ChromaDB 企业知识检索、SSE 与前端恢复代码存在，待本地迁移和人工验收。LLM/RAG 禁用或故障时继续使用确定性流程与明确回退；LangGraph 和真实面试评价 Agent 仍为计划中。

数据库层已建立 SQLAlchemy ORM、Alembic 配置和迁移链，最新 revision 为 `0004_agent_runtime`。本次未执行迁移；演示数据与结构迁移分离，部署结果仍待本地人工验收。

## 项目定位

TalentFlow 通过一套 FastAPI 后端支撑 Vue Web 管理端、微信小程序员工端和 Gradio 内部调试台。系统围绕招聘决策、员工服务、考勤事实、薪资预审、权限审计和 Agent Trace 建设，强调可解释、可追溯和权限隔离。

## 核心能力

- 招聘决策：岗位画像、候选人评分、权重沙盘、候选人比较、招聘流程和面试排期。
- 员工服务：年假、制度、本人薪资摘要和员工服务 Agent。
- 考勤：员工签到、签退、今日考勤状态和本月考勤摘要。
- 薪资预审：HR 查看预审明细、扣款来源、异常解释和待 HR 确认状态。
- 权限审计：薪资访问控制、字段脱敏、敏感访问日志和 `trace_id`。
- Agent 能力：招聘策略、确定性简历解析、岗位匹配、规则式决策审查和结构化 HR 最终报告代码存在，待本地人工验收；Runner 通过应用级容器注入 Tool，企业知识仍使用 `LOCAL_HYBRID_FALLBACK`。真实 LLM Provider、Embedding、文档 Loader、ChromaDB 和 Agent 对真实 LLM/RAG 的调用均为计划中。

## 端与边界

- Vue Web 管理端：HR 招聘、排期、薪资预审、审计、驾驶舱，以及员工相关查询入口。
- 微信小程序员工端：Sprint 3 规划中的员工端入口，仅提供签到、签退、考勤摘要、年假余额、本人薪资摘要和制度查询。
- Gradio：仅作为内部 Agent 调试台，不作为正式业务入口。
- Web、小程序和 Gradio 共享同一套 FastAPI 后端。

## AI 禁飞区

以下三个核心算法文件及其核心测试由人工负责人编写，AI 不得创建或修改：

- `backend/app/human_only/resume_scoring.py`
- `backend/app/human_only/interview_scheduler.py`
- `backend/app/human_only/salary_access_control.py`

核心测试文件：

- `backend/tests/human_only/test_resume_scoring.py`
- `backend/tests/human_only/test_interview_scheduler.py`
- `backend/tests/human_only/test_salary_access_control.py`

工程调用链必须分离：

- 普通请求：`API -> Service -> Repository -> PostgreSQL`。
- Agent 任务：`Agent -> Tool -> Service -> human_only`。

## 技术栈

| 技术                        | 用途                  |
| --------------------------- | --------------------- |
| Vue 3 + TypeScript + Vite   | Web 管理端            |
| FastAPI + Python 3.12       | 一套共享后端          |
| PostgreSQL                  | 结构化业务数据        |
| 规则式异步 Runtime + SSE    | Sprint 2.3 确定性招聘工作流与实时事件 |
| LangGraph + LangChain Tools | 后续 Agent 编排规划   |
| ChromaDB                    | 后续企业制度 RAG 规划 |
| Gradio                      | 内部 Agent 调试台     |
| Docker Compose + Nginx      | Sprint 3 计划部署目标 |

## 系统架构

```mermaid
flowchart LR
    Web[Vue Web 管理端]
    Mini[微信小程序员工端]
    Gradio[Gradio 内部调试台]
    API[一套 FastAPI 后端]
    Service[Service]
    Repo[Repository]
    DB[(PostgreSQL)]
Agent[Agent Runtime]
    Tool[Tools]
    RAG[(后续 ChromaDB RAG)]
    Human[AI 禁飞区]

    Web --> API
    Mini --> API
    Gradio --> API
    API --> Service
    Service --> Repo
    Repo --> DB
    API --> Agent
    Agent --> SSE[真实 SSE AgentEvent]
    Agent --> Tool
    Tool --> Service
    Tool --> RAG
    Service --> Human
```

## 招聘多 Agent 正式架构

```text
企业招聘目标
→ 招聘策略 Agent
→ 简历解析 Agent / 岗位匹配 Agent / 面试评估 Agent
→ 决策审查 Agent
→ HR 最终报告
→ HR 人工决定
```

| 状态 | 范围 |
| --- | --- |
| 代码存在，待本地人工验收 | PostgreSQL RunStore、招聘策略、确定性简历解析、岗位匹配、决策审查、LLM 报告增强、ChromaDB RAG、SSE、Agent API 与前端实时看板 |
| 已建立目录或契约 | 面试评估节点、候选人/证据/审查/报告类型、员工服务与薪资预审 |
| 计划中 | LangGraph、真实面试评价 Agent、员工服务 Agent、薪资预审助手 |

当前阶段为 `SPRINT_2_3_INTEGRATED`，下一阶段为 `END_TO_END_VALIDATION`。企业知识正常时使用 `CHROMA_HYBRID`，失败或禁用时使用 `LOCAL_HYBRID_FALLBACK`；策略与报告模型增强失败时使用 `RULE_BASED_FALLBACK`。面试评估无真实数据时仍以 `STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE` 标记为 `SKIPPED`。Agent 不直接访问 Repository 或 `human_only`，最终决定由 HR 完成。

## 项目结构

```text
.
├── AGENTS.md
├── .agent/
├── docs/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── modules/
│   │   │   ├── recruitment/
│   │   │   │   ├── intelligence/     # 招聘智能分析纯数据契约
│   │   │   │   └── services/         # 上下文、匹配、审查与报告 Service
│   │   │   └── */models.py
│   │   ├── agents/
│   │   │   ├── runtime/              # Store 契约、Runner 与 SSE
│   │   │   ├── shared/               # 状态、事件、来源、Guardrail、模型网关契约
│   │   │   ├── workflows/            # 招聘、员工服务、薪资预审工作流契约
│   │   │   ├── tools/                # Tool 契约、兼容入口与 Service 委托
│   │   │   └── prompts/              # Prompt 边界说明
│   │   ├── rag/
│   │   │   ├── ingestion/            # 摄取 Protocol，未接入真实索引
│   │   │   └── retrieval/            # 检索与引用 Protocol，未接入真实检索
│   │   ├── shared/
│   │   ├── human_only/
│   │   └── agent_console/
│   ├── alembic/
│   │   └── versions/
│   └── tests/
├── frontend/
├── miniprogram/
├── data/
├── infra/
└── scripts/
```

## 开发规范

- 只使用 `dev` 和 `main`。
- 禁止直接向 `main` 提交。
- Commit 类型使用 `feat`、`fix`、`docs`、`refactor`。
- 修改架构、需求、接口、数据模型、权限或薪资规则时同步更新 docs 与 `.agent`。
- 遵守根目录与各子目录分层 `AGENTS.md` 约束。
- 不提交真实 `.env`、真实密钥、真实企业数据和本地运行产物。

## 计划运行方式

当前命令仅作为计划运行方式，需待对应脚手架和配置完成后使用。

```powershell
conda activate talentflow
pip install -r backend/requirements-dev.txt

cd frontend
npm install
npm run dev
```

后端计划端口：`8000`。前端计划端口：`5173`。小程序局域网调试需使用笔记本局域网 IP，不使用 `localhost`。

数据库迁移计划由团队成员在本地后端目录手动执行：

```powershell
cd "你的本地后端文件路径"
alembic upgrade head
```
