# AI 禁飞区核心算法接口契约

本文档约定 `backend/app/human_only/` 下三个人工手写核心模块的工程接口。工程外层已按这些契约完成 API、Service、前端调用和缺失状态处理。

## 通用约定

- 三个核心实现文件只能由人工负责人创建和维护。
- 禁飞区函数只接收结构化 `dict` 输入，只返回结构化 `dict` 结果。
- 禁飞区不得依赖 FastAPI、SQLAlchemy、LangGraph、ChromaDB、HTTP 客户端、数据库连接或 LLM。
- 缺失文件、缺失函数或函数抛出 `NotImplementedError` 时，Service 返回 `status: "algorithm_not_ready"`。

## 简历评分

- 文件：`backend/app/human_only/resume_scoring.py`
- 函数：`score_resume(payload: dict) -> dict`
- Service：`RecruitmentService.score_application(...)`
- API：`POST /api/v1/recruitment/applications/{application_id}/score`

输入包含：

- `job`：岗位 ID、标题、必备技能、加分技能、最低经验月数。
- `candidate`：候选人 ID、姓名、技能、经验月数、到岗时间、结构化画像。
- `weights`：技能、项目、到岗时间、风险等评分权重。

返回建议包含：

- `score_total`：综合评分。
- `match_score`：岗位匹配度。
- `skill_match`：技能匹配说明。
- `experience_match`：经验匹配说明。
- `risk_tags`：风险标签列表。
- `risk_prompt`：风险提示。
- `recommended_action`：推荐动作。
- `scoring_basis`：评分依据列表。
- `score_breakdown`：分项评分。

## 智能面试排期

- 文件：`backend/app/human_only/interview_scheduler.py`
- 函数：`schedule_interview(payload: dict) -> dict`
- Service：`InterviewService.preview_schedule(...)`
- API：`POST /api/v1/interviews/schedule/preview`

输入包含：

- `application_id`：候选人申请 ID。
- `candidate.available_slots`：候选人可用时间段。
- `interviewers`：面试官、专长和可用时间段。
- `meeting_rooms`：会议室和可用时间段。
- `duration_minutes`：面试时长。

返回建议包含：

- `recommended_time`：推荐面试时间段。
- `recommended_interviewer_id`：推荐面试官 ID。
- `recommended_room_id`：推荐会议室 ID。
- `interviewer_availability`：面试官可用时间说明。
- `candidate_availability`：候选人可用时间说明。
- `conflict_detection`：冲突检测说明。
- `recommendation_reason`：推荐理由。

## 薪资权限校验与预审

- 文件：`backend/app/human_only/salary_access_control.py`
- 函数：`check_salary_access(payload: dict) -> dict`
- Service：`PayrollPreAuditService.review_pre_audit(...)` 调用 `PayrollAccessService.check_salary_access(...)`
- API：`POST /api/v1/payroll-review/pre-audit`

输入包含：

- `requester`：请求人角色和员工 ID。
- `records`：薪资预审记录、员工、周期、收入、扣款、预览实发、计算快照、明细项。

返回建议包含：

- `pending_batches`：待预审批次数。
- `abnormal_salary_items`：异常薪资项列表。
- `permission_risks`：权限风险列表。
- `deduction_sources`：扣款来源说明列表。
- `approval_suggestion`：HR 审批建议。
- `risk_level`：风险等级。
