# AI 使用日志：刘子恒

**日期：** 2026-07-15  
**涉及阶段：** Sprint 1 基础平台开发；Sprint 2 Agent/RAG 与后端自动化测试  
**当前状态：** 代码存在，待本地人工验收。

> 说明：本日志记录 AI 辅助时的提问、回答、实际解决的问题，以及 AI 输出中发现的错误或局限。Sprint 1 内容依据 `docs/计划.md` 中刘子恒的职责范围整理；最终代码、环境、数据库和验收结果均由组员人工确认。

## Sprint 1：基础平台开发

## 1. 如何划分 FastAPI 后端基础平台的职责？

### 我问了什么

如何为 TalentFlow 建立 FastAPI 基础平台，并保证 Web 管理端、微信小程序员工端和 Gradio 内部调试台共享同一套后端，同时保持普通业务请求遵守 `API -> Service -> Repository -> PostgreSQL`？

### AI 回答什么

AI 建议采用模块化单体：由 `main.py` 和 API Router 聚合入口；`core/` 放置配置、数据库、异常、安全和依赖；`shared/` 放置统一响应、分页和 trace；业务模块分别维护 Service 与 Repository。并说明 Gradio 只作为内部调试入口，不增加第二套后端。

### 解决什么问题

- 为 Sprint 1 的基础平台、API 聚合、统一响应和 trace 边界提供目录与分层参考。
- 明确 Web、小程序和 Gradio 共用同一 FastAPI 后端的约束。
- 明确 Route 不直接访问 Repository 或 `human_only`。

### AI 犯了什么错，以及如何纠正

- AI 的初始方案偏向通用工程模板，未先突出本项目“只允许一套后端、禁止微服务”的限制。
- 人工根据项目约束收窄方案：不引入第二后端、Redis、Celery、RabbitMQ 或 Kubernetes，并以模块化单体作为唯一实现方向。

## 2. 如何处理认证、权限和统一错误响应？

### 我问了什么

如何让登录、权限校验、统一响应和 `trace_id` 在各业务接口中保持一致，同时避免 API 层泄漏底层异常？

### AI 回答什么

AI 建议将认证、当前用户依赖、异常处理和响应封装放入公共基础层；业务接口调用 Service，由统一错误处理转换为包含错误码和 `trace_id` 的响应。

### 解决什么问题

- 为认证、权限依赖、统一错误结构和审计追踪提供实现边界。
- 为后续考勤、薪资、审计和招聘接口复用同一响应规范提供参考。

### AI 犯了什么错，以及如何纠正

- AI 初始回答只强调“统一异常处理”，没有把权限判断必须以服务端结果为准、敏感数据不写入 Trace 的要求拆开说明。
- 人工补充并审查权限和审计边界：权限以服务端为准，日志不记录密码、密钥、完整简历或完整薪资数据。

## Sprint 2：Agent/RAG 与自动化测试

## 3. 核心测试应覆盖哪些模块和异常路径？

### 我问了什么

如何在不连接真实 PostgreSQL、LLM、ChromaDB 或网络服务的前提下，为考勤规则、权限归一化、Agent Guardrail、RAG 分块和 Agent RunStore 补充分模块自动化测试，并覆盖异常路径、极端输入和轻量并发场景？

### AI 回答什么

AI 建议按功能拆分测试文件，优先使用纯函数、内存对象、Fake Repository、Mock 和 `InMemoryAgentRunStore`；同时覆盖时间边界、非法配置、权限归一化、订阅关闭、容量上限、深拷贝和并发隔离等场景。

### 解决什么问题

- 建立 `backend/tests/unit/modules/`、`backend/tests/unit/agents/`、`backend/tests/unit/rag/` 与 `backend/tests/concurrency/` 的测试分类。
- 为核心模块建立异常路径与极端输入测试，不依赖真实外部基础设施。
- 在 `pytest-core.ini` 中集中维护核心测试入口和覆盖率目标。

### AI 犯了什么错，以及如何纠正

- AI 最初沿用补丁中的预置覆盖率数字，但这些数字并非当时环境实际执行得到的结果。
- 人工指出后，AI 将测试文档改为“代码存在，待本地人工验收”，并区分已执行结果与因依赖缺失未执行的结果。

## 4. Agent Guardrail 为什么会误伤合法导入？

### 我问了什么

为什么 `import_path.startswith(FORBIDDEN_DIRECT_IMPORTS)` 会错误拒绝 `app.core.database_helpers`、`app.human_only_adapter` 等合法模块？如何验证修复有效？

### AI 回答什么

AI 说明字符串前缀判断不能识别 Python 模块边界。应仅拒绝禁止模块本身，或以“禁止模块名加 `.`”开头的真实子模块；并通过临时缺陷注入验证同前缀合法模块会失败。

### 解决什么问题

- 在 `backend/app/agents/shared/guardrails.py` 中保留模块边界判断修复。
- 新增 Guardrail 测试，区分禁止模块、真实子模块、同前缀合法模块、空字符串和普通模块。
- 在 `docs/测试异常路径与缺陷注入记录.md` 中记录缺陷注入方式、失败原因、修复代码与回归步骤。

### AI 犯了什么错，以及如何纠正

- AI 第一次整理缺陷注入说明时，给出了“只检查完全相等模块名”的替代错误版本，没有严格采用本次需要复现的 `startswith(...)` 错误写法。
- 人工指出后，AI 将注入代码改为原始前缀匹配错误写法，并记录四个同前缀合法模块被误拒绝的原因。

## 5. 并发测试如何同时体现 Backend、数据库和 LLM 请求？

### 我问了什么

如何让 RAG 并发测试不仅验证 splitter 的线程安全，还能体现 Backend 请求、数据库查询和 LLM 请求，并分别输出请求次数、处理时间和吞吐量？

### AI 回答什么

AI 建议采用不联网的内存调用链：`Backend 请求 -> Repository 查询 -> RAG splitter -> ModelGateway`。Repository 和 ModelGateway 使用线程安全替身，但 LLM 输入和输出沿用 `ModelGatewayInput`、`ModelGatewayOutput` 契约；三类请求分别计数、计时和输出。

### 解决什么问题

- 更新 `backend/tests/concurrency/test_splitter_concurrency.py`。
- 使用 8 个线程执行 64 个请求，检查每次结果一致、无共享状态污染。
- 并发输出分为 Backend、数据库和 LLM 三类指标；测试不发送真实数据库或 LLM 请求。

### AI 犯了什么错，以及如何纠正

- AI 的第一版并发测试只对 splitter 做并发调用，且 LLM 替身直接接收 chunks，无法体现后端请求边界和合理的模型请求结构。
- 人工指出“请求数据太假、结果需要分开输出”后，AI 改为 Backend、Repository、RAG 和 ModelGateway 的内存链路，并使用结构化模型输入/输出契约。

## 6. 如何补齐业务模块测试？

### 我问了什么

如何让 `analytics`、`attendance`、`audit`、`auth`、`employee`、`interview`、`notification`、`payroll`、`policy` 和 `recruitment` 在 `tests/unit/modules/` 下均有对应测试文件，同时不为测试虚构新的生产业务代码？

### AI 回答什么

AI 建议优先测试已有 Service 层、模型契约和已有降级分支：使用 Fake Repository 检查考勤、员工年假、审计序列化、账号状态、面试时间校验、政策分类、薪资预审 JSON 转换和招聘人工复核边界。对于当前没有独立 Service 的 analytics 与 notification，仅验证既有模块/模型契约。

### 解决什么问题

- 为上述模块补充或完善 `tests/unit/modules/test_<module>_*.py` 文件。
- 测试均使用内存对象或 Mock，不访问真实 PostgreSQL。
- 不修改三个 AI 禁飞区算法文件及其核心测试文件。

### AI 犯了什么错，以及如何纠正

- AI 起初只补充了核心模块测试，未覆盖全部业务模块目录，也没有单独说明 analytics 和 notification 当前缺少独立 Service 逻辑。
- 人工提出模块覆盖要求后，AI 为每个模块增加至少一个测试文件；对没有独立业务 Service 的模块，只测试现有导入或模型契约，不新增虚构生产功能。

## 使用边界与人工确认

- AI 仅协助测试代码、测试配置、测试说明和日志整理。
- 简历评分、面试排期和薪资访问控制的核心算法及其核心测试保持人工维护，未由 AI 修改。
- Agent 相关测试遵守 `Agent -> Tool -> Service -> human_only` 边界；Agent 不直接访问 Repository 或 `human_only`。
- 最终代码审查、完整依赖环境测试和验收由组员人工完成。

## 总结与反思

### AI 帮助完成了什么

- 根据现有代码结构整理核心测试范围，并将考勤、权限、Guardrail、RAG 分块、RunStore 和业务模块测试按目录拆分。
- 协助定位 Guardrail 的字符串前缀误判风险，给出按 Python 模块边界判断的修复方向，并补充缺陷注入与回归测试说明。
- 协助把并发测试从单纯 splitter 调用扩展为 Backend、Repository、RAG splitter 和 ModelGateway 的内存调用链，并分别输出指标。
- 协助使用 Fake Repository、内存对象和 Mock 编写业务单测，避免测试依赖真实 PostgreSQL、LLM、ChromaDB 或网络服务。
- 协助整理异常路径、极端输入、测试配置、测试文档和当日工作日志。

### AI 没帮上忙或做错了什么

- AI 初次整理补丁时沿用了未经当前环境执行验证的覆盖率数字；后续已改为明确区分“代码存在，待本地人工验收”和已实际观察到的结果。
- AI 第一次描述 Guardrail 缺陷注入时给出了不完全等同于目标缺陷的错误版本；后续改为使用实际的 `startswith(FORBIDDEN_DIRECT_IMPORTS)` 误判场景。
- AI 的第一版并发测试只覆盖 splitter，且模拟 LLM 输入过于简单，不能体现 Backend、数据库与模型网关边界；在人工反馈后已重构。
- AI 无法替代完整依赖环境、真实数据库、真实模型服务和人工业务验收；这些内容没有被写成已经完成或已经通过。
- AI 不应参与三个 `human_only` 核心算法及其核心测试的实现和修改，相关工作保持人工维护。

### 踩过的坑

- `origin` 远程地址与指定 GitHub 仓库不一致，不能在未确认来源前直接拉取。
- 当前执行环境缺少部分开发依赖时，RAG、招聘和面试模块的导入链会被 `python-docx`、`pypdf` 等依赖阻断。
- pytest 成功测试默认捕获标准输出；并发指标需要通过 pytest 终端报告器输出，才能在 `-q` 命令下展示。
- 未注册自定义 pytest marker 会产生警告；不必要的 marker 应移除或在配置中登记。
- `pytest-core.ini` 使用显式 `testpaths` 时，新测试文件必须同步加入，否则不会被核心测试命令执行。
- 并发测试中的内存替身只能验证调用契约、结果稳定性和共享状态隔离，不能代表真实 PostgreSQL 或真实 LLM 的性能。

### 学到的经验

- 边界测试应优先覆盖“恰好等于阈值、刚超过阈值、空值、非法类型、超长输入、并发访问和权限越界”。
- 对模块名、路径、权限码等字符串判断时，应按领域边界而非简单前缀判断，避免误伤合法输入。
- 测试输出需要区分“端到端墙钟时间”“单类请求累计时间”和“平均耗时”，否则吞吐量数据容易被误解。
- 单元测试应优先依赖纯函数、Fake Repository 和明确的契约对象；外部服务的行为使用可审计替身模拟。
- 测试文档必须如实区分已执行结果、环境阻断和待人工验收事项，不能把计划或预置结果写成事实。
- 新增测试不仅要能单独运行，还要纳入统一测试入口、覆盖率配置和相关文档，才能避免回归遗漏。
