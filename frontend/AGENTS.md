# frontend 前端约束

## 覆盖范围

本文件约束 Vue Web 管理端。

## 架构规则

- 使用 Vue 3 + TypeScript + Vite。
- Web 管理端只调用同一套 FastAPI 后端。
- 当前静态视觉原型可以使用本地 mock 数据；接入后端前不得伪造 API 成功状态。
- 共享组件放入 `src/shared/components/`。
- 全局布局放入 `src/layouts/`。
- 业务功能放入 `src/features/`。
- 招聘相关功能统一放入 `src/features/recruitment/`。
- 员工端相关 Web 功能放入 `src/features/employee/`。

## 禁止事项

- 不在前端保存真实密钥、数据库连接或 JWT 密钥。
- 不在小程序范围内实现 HR 招聘、排期、薪资预审或审计后台。
- 不直接访问禁飞区或数据库。
- 不引入与既定方案无关的框架。
