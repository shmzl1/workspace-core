# Agent Tool 边界

Tool 只能调用 Service，不访问 Repository、不导入 `human_only`。新增的招聘、面试、知识和薪资文件当前只包含 `ToolContract` 与 Protocol，不执行知识检索、招聘评分、面试排期或薪资确认。

`employee_service.py` 中三个现有兼容函数仍被普通测试使用，暂时保留；新 Runtime 不应直接注入 SQLAlchemy Session。后续迁移必须先提供等价 Service 注入边界，再移除兼容入口。

当前状态：招聘、面试、知识和薪资 Tool 为“已建立目录或契约”；员工旧入口代码存在，待本地人工验收。
