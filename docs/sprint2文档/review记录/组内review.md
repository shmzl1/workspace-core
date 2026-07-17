# Sprint 2 组内Review 记录

## 一、审查重点：

- 业务流程是不是正确的
- 前后端路由之类的是否一致
- 异常与边界输入处理有没有

## 二、Review 安排

主要负责后端的刘子恒和黄钧互相review，主要负责前端的吴越和唐丞杰互相review

---

# 三、7月13日 Review 记录

## 3.1 黄钧对刘子恒的代码 Review

### 审查范围

1. `backend/app/human_only/resume_scoring.py`
2. `backend/app/human_only/interview_scheduler.py`
3. `backend/tests/human_only/test_resume_scoring.py`
4. `backend/tests/human_only/test_interview_scheduler.py`
5. 招聘评分与面试排期相关 Service 调用边界

### Review结果

1. **必备技能和加分技能未分开处理**

   - 涉及位置：`resume_scoring.py` 中的 `score_resume()`。
   - 问题说明：当前代码将 `required_skills` 和 `preferred_skills` 合并计算。候选人缺少加分技能时，也会进入 `missing_skills`，并被标记为“关键技能缺失”。
   - 修改建议：分别处理必备技能和加分技能。只有缺少 `required_skills` 时生成“关键技能缺失”风险；缺少 `preferred_skills` 时只影响加分结果。
2. **面试时长缺少异常输入校验**

   - 涉及位置：`interview_scheduler.py` 中 `duration_minutes` 的读取逻辑。
   - 问题说明：当前代码直接执行 `int(duration_minutes)`。非法字符串会触发异常，零或负数也可能继续进入排期计算。
   - 可能影响：错误请求可能导致接口异常，或者生成结束时间早于开始时间的不合理排期。
   - 修改建议：捕获类型转换异常，并将面试时长限制在合理范围内，例如 15 至 240 分钟。非法输入统一返回 `invalid_input`。
3. **时间格式可能出现时区混用问题**

   - 涉及位置：`parse_time()` 和 `overlap()`。
   - 问题说明：输入时间既可能带时区，也可能不带时区。带时区和不带时区的 `datetime` 对象进行比较时可能失败。
   - 可能影响：部分候选人、面试官或会议室时间格式不一致时，排期算法可能抛出异常。
   - 修改建议：在时间解析入口统一时区规则，将所有时间转换为统一时区，或者明确拒绝混合格式。
4. **边界测试覆盖不足**

   - 涉及位置：两个禁飞区算法测试文件。
   - 问题说明：当前已覆盖高匹配、技能缺失、经验不足、时间冲突和无交集等基础情况，但部分异常输入尚未覆盖。
   - 修改建议：补充以下测试：

     1. 仅缺少加分技能时不产生关键技能风险。
     2. `profile_json` 为字符串或列表时不崩溃。
     3. 带时区和不带时区时间混用。

### 结论

1. 当前主要问题集中在业务规则区分和异常输入校验。
2. 结论：有条件通过。

审查人：黄钧
被审查人：刘子恒
初次审查日期：2026年7月13日

---

## 3.2 刘子恒对黄钧负责的代码 Review

### 审查范围

1. `backend/app/agents/runtime/recruitment_runner.py`
2. `backend/app/modules/agent_runtime/service.py`
3. `backend/app/api/v1/endpoints/agent.py`
4. `backend/app/human_only/salary_access_control.py`
5. Agent Run、SSE、人工复核和薪资权限调用链

### Review 意见

1. **Agent Run 运行时对象缺少清理机制**

   - 涉及位置：`PostgreSQLAgentRunStore`。
   - 问题说明：`_run_locks` 会持续保存运行锁，`cleanup_expired()` 当前固定返回 `0`，没有实际清理逻辑。
   - 可能影响：长时间运行时可能积累无用锁和运行状态对象。
   - 修改建议：Run 进入终态且没有订阅者后，删除对应运行锁；补充过期对象清理逻辑。
2. **异常处理缺少服务端详细日志**

   - 涉及位置：`recruitment_runner.py` 中的 `except Exception`。
   - 问题说明：对外返回的错误已经进行了统一化，但服务端没有记录原始错误。
   - 可能影响：出现运行失败时，只能看到公共错误码，难以定位具体原因。
   - 修改建议：在服务端日志中记录异常类型，失败节点和失败步骤。
3. **薪资访问函数职责混合**

   - 涉及位置：`salary_access_control.py` 中的 `check_salary_access()`。
   - 问题说明：当参数为字符串时，函数执行薪资字段访问判断；当参数为字典时，又直接返回薪资预审结果。一个函数包含两种完全不同的业务含义和返回结构。
   - 修改建议：拆分为 `check_salary_access()` 和 `review_salary_records()` 两个独立函数。

### 审查结论

1. 问题集中在锁对象清理，异常可观测性和函数功能聚合上。
2. 审查结论：有条件通过。

审查人：刘子恒
被审查人：黄钧
初次审查日期：2026年7月13日

---

# 四、7月14日 Review 记录

## 4.1 唐丞杰对吴越的代码 Review

### 审查范围

1. `frontend/src/features/recruitment/evaluation/composables/useRecruitmentAgentRun.ts`
2. `frontend/src/shared/api/modules/agent.ts`
3. 多 Agent 工作流看板
4. Agent 事件列表和节点详情组件
5. 招聘结果和 HR 报告展示组件
6. SSE 连接、恢复和错误状态处理

### Review 意见

1. **节点完成后当前 Agent 状态可能没有及时清空**

   - 涉及位置：`useRecruitmentAgentRun.ts` 中的 `applyEvent()`。
   - 问题说明：收到 `AGENT_COMPLETED` 时只清空了 `current_candidate_id`，没有同步清空 `current_agent` 和 `current_node`。
   - 修改建议：节点完成且暂时没有后续节点运行时，清空当前 Agent 和节点；也可以主动重新读取 Snapshot，以后端状态为准。
2. **SSE 单个事件解析失败会中断整个事件流**

   - 涉及位置：`agent.ts` 中的 `emitSseBlock()`。
   - 问题说明：当前直接对 SSE 数据执行 `JSON.parse()`，没有对单个事件块增加异常捕获。
   - 修改建议：对每个事件块单独使用 `try/catch`。解析失败时跳过异常块，并继续处理后续事件。
3. **实时连接中断后缺少自动恢复**

   - 涉及位置：SSE 的 `onError` 处理逻辑。
   - 问题说明：连接失败后只显示错误信息，没有自动刷新 Snapshot，也没有重连机制。
   - 修改建议：连接异常后先刷新一次 Snapshot，再进行有限次数的自动重连，并使用逐步增加的等待时间。
4. **事件摘要缺少运行时字段校验**

   - 涉及位置：`applyEvent()` 中对 `knowledge_summary`、`job_match_summary`、`decision_review` 和 `report` 的处理。
   - 问题说明：目前只判断数据是否为对象，然后直接进行 TypeScript 类型断言。
   - 修改建议：确认关键字段存在后再更新 Snapshot。

### 审查结论

1. 问题主要在断流恢复和待人工复核状态下的前端状态同步。
2. 结论：有问题但不多。

审查人：唐丞杰
被审查人：吴越
初次审查日期：2026年7月14日

---

## 4.2 吴越对唐丞杰的代码 Review

### 审查范围

1. `frontend/src/features/auth/authStore.ts`
2. `frontend/src/features/auth/LoginView.vue`
3. `frontend/src/app/router/guards.ts`
4. `frontend/src/shared/api/apiClient.ts`
5. `frontend/src/views/AttendanceView.vue`
6. 登录、权限路由、员工考勤和公共错误处理

### Review 意见

1. **网络异常会直接清除用户登录状态**

   - 涉及位置：`authStore.ts` 中的 `loadCurrentUser()`。
   - 问题说明：当前捕获任何异常后都会调用 `clearSession()`。后端临时不可用或网络短暂断开时，用户也会被强制退出。
   - 修改建议：只有在返回 401、Token 无效、Token 过期或账号停用时清除会话。网络异常时保留当前会话，并提示后端暂时不可用。
2. **无权限路由跳转缺少明确提示**

   - 涉及位置：`guards.ts`。
   - 问题说明：用户没有目标页面权限时，会直接跳转到默认页面，不会说明跳转原因。
   - 修改建议：跳转时携带权限提示，或者统一进入 403 权限拒绝页面。
3. **考勤目标员工选择权限不明确**

   - 涉及位置：`AttendanceView.vue` 中的 `canSelectTarget`。
   - 问题说明：当前使用薪资、审计和员工部门权限判断是否可以选择其他员工，没有使用明确的考勤管理权限。
   - 修改建议：新增并统一使用 `attendance.department.read` 或 `attendance.manage` 权限。
4. **考勤页面多个请求一起**

   - 涉及位置：`loadAttendancePage()`。
   - 问题说明：员工姓名、今日考勤和周汇总通过一个 `Promise.all` 同时加载。任意一个辅助请求失败，整个页面都会进入错误状态。
   - 修改建议：将员工姓名作为非关键请求单独处理；今日考勤和周汇总也可以分别展示错误状态。

### 审查结论

1. 当前问题是网络异常导致强制退出，以及考勤管理权限语义不明确。
2. 审查结论：有条件通过。

审查人：吴越
被审查人：唐丞杰
初次审查日期：2026年7月14日

---

# 五、Review 汇总结论

1. 本轮 Review 已覆盖以下核心模块：
   - 招聘评分
   - 智能面试排期
   - 多 Agent 招聘工作流
   - Agent Run 持久化
   - 人工审批
   - 薪资权限控制
   - SSE 实时事件
   - 登录
   - 路由权限
   - 员工考勤
2. 黄钧待处理问题：
   - 必备技能和加分技能分离。
   - 异常数据类型检查。
   - 面试时长和时区边界校验。
3. 刘子恒待处理问题：
   - 多进程审批并发控制。
   - 运行锁清理。
   - 服务端异常日志。
   - 薪资权限函数职责拆分。
4. 吴越待处理问题：
   - 待人工复核状态同步。
   - SSE 解析容错。
   - 断流恢复和事件列表性能。
5. 唐丞杰待处理问题：
   - 网络异常时的会话处理。
   - 考勤权限语义。
   - 登录校验。
   - 页面请求解耦。

## 六、处理要求

    修改完成后先自己手动验收，再让原审查人执行复审。
