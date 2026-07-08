# backend/app/modules/payroll 薪资模块约束

## 覆盖范围

本文件约束薪资查询、薪资预审、薪资确认、字段脱敏与审计相关工程代码。

## 固定边界

- 薪资预审由规则引擎计算。
- AI 只负责异常解释、总结和审查建议。
- HR 负责最终确认。
- 所有薪资读取必须经过权限校验。
- 所有薪资预审、确认、拒绝和敏感查询必须写入审计日志。
- 普通薪资业务请求遵循 `API -> Service -> Repository -> PostgreSQL`。
- 普通薪资业务调用权限核心算法遵循 `API -> Service -> human_only`。
- Agent 薪资任务调用权限核心算法遵循 `Agent -> Tool -> Service -> human_only`。

## 固定状态

草稿
-> 已生成预审
-> 待 HR 确认
-> 已确认

## 服务职责

- 只有 `confirmation_service` 可以改为“已确认”。
- `calculation_service` 只生成预览。
- 所有薪资读取先经 `access_service`。
- `salary_access_control.py` 的 `human_only` 公开函数为 `check_salary_access(...)`。
- `access_service` 可以包装为 Service 层 `check_salary_access(...)`，并作为工程代码访问薪资权限算法的唯一入口。
- Agent Tool 只能调用 Service 层函数，不能直接调用 `human_only` 函数。
- 每项扣款记录考勤来源、规则依据和计算过程。
- 预审、确认、拒绝、敏感查询都写审计。
- 不做银行发薪、税务、社保、公积金。

## 禁止事项

- Agent 不得确认工资。
- Agent 不得修改工资。
- Agent 不得删除扣款。
- Agent 不得写入已确认薪资。
- payroll 只读取考勤事实和月度汇总，不反向修改原始考勤记录。
- Route/API 不直接访问数据库，不直接调用 `human_only`。
- Agent 不直接访问 Repository，不直接调用 `human_only`。
- AI 不得创建、修改、移动、删除、格式化、补全 `backend/app/human_only/salary_access_control.py` 或其核心测试。
- 不自动执行数据库迁移、Docker 启动、服务启动或构建命令；`alembic upgrade head` 必须由人工确认后执行。
