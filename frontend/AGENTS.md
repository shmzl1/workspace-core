# frontend 前端约束

## 覆盖范围

本文件约束 Vue Web 管理端。

## 架构规则

- 使用 Vue 3 + TypeScript + Vite。
- Web 管理端只调用同一套 FastAPI 后端，与微信小程序员工端、Gradio 内部调试台共享后端业务 Service。
- 后端采用模块化单体，不拆微服务，不新增第二套后端。
- 当前静态视觉原型可以使用本地 mock 数据；接入后端前不得伪造 API 成功状态。
- 共享组件放入 `src/shared/components/`。
- 所有公共请求通过 `src/shared/api/`。
- 全局布局放入 `src/layouts/`。
- 业务功能放入 `src/features/`。
- 招聘相关功能统一放入 `src/features/recruitment/`。
- 员工端相关 Web 功能放入 `src/features/employee/`。
- 页面按 `recruitment`、`employee`、`payroll-review` 等 feature 组织。
- 异步页面必须有加载、空、错误和权限拒绝状态。
- mock 仅用于开发兜底。

## 禁止事项

- 不在前端保存真实密钥、数据库连接或 JWT 密钥。
- 前端不做最终权限判断。
- 前端不计算正式薪资。
- 权限与金额以服务端返回为准。
- 不在小程序范围内实现 HR 招聘、排期、薪资预审或审计后台。
- 不直接访问禁飞区或数据库。
- 不直接访问底层算法，不绕过后端 Service。
- 不引入与既定方案无关的框架。
- 不引入 Redis、Celery、RabbitMQ、Kubernetes 或第二套后端相关目录。
- 前端开发不要自动执行 `npm run dev`；默认不运行 npm、Docker、Git、构建或启动命令，除非用户明确要求。
