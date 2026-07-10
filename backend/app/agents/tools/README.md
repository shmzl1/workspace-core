# Agent Tool 边界

Tool 只能调用 Service，不访问 Repository、不导入 `human_only`。Sprint 2.2 的候选人画像 Tool 与企业知识 Tool 分别调用 `ResumeProfileService` 和 `RecruitmentKnowledgeService`；不执行招聘评分、面试排期、薪资确认、LLM 或 ChromaDB 检索。

`employee_service.py` 中三个现有兼容函数仍被普通测试使用，暂时保留；新 Runtime 不应直接注入 SQLAlchemy Session。后续迁移必须先提供等价 Service 注入边界，再移除兼容入口。

当前状态：Sprint 2.2 简历与知识 Tool 代码存在，待本地人工验收；岗位匹配、面试和薪资 Tool 为“已建立目录或契约”；员工旧入口代码存在，待本地人工验收。
