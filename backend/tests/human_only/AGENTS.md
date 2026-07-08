# backend/tests/human_only 禁飞区测试约束

## 覆盖范围

本文件约束 `backend/tests/human_only/`。

## 禁飞区核心测试

AI 禁飞区核心测试只包含以下三个文件，并且只能由人工负责人创建和维护：

- `backend/tests/human_only/test_resume_scoring.py`
- `backend/tests/human_only/test_interview_scheduler.py`
- `backend/tests/human_only/test_salary_access_control.py`

## 严格禁止

- AI 不得创建、修改、移动、删除、格式化或补全上述测试文件。
- AI 不得生成禁飞区核心算法的测试用例实现。
- AI 不得复制、重写、模拟或绕过禁飞区核心算法来生成测试。

## 允许范围

AI 可在其他测试目录中为 Service、API、Agent Tool、RAG 和权限流程编写普通测试，但不得复制禁飞区算法逻辑。

允许在用户明确要求时运行测试；默认不自动运行 pytest、数据库迁移、Docker、服务启动或构建命令。
