# 面试评估 Agent

- 职责：基于真实结构化面试数据形成评价。
- 允许输入：`InterviewEvaluationInput`。
- JSON 输出：`InterviewEvaluationSummary`。
- 未知信息：无真实面试数据时只返回待面试/`SKIPPED` 语义。
- 禁止：伪造面试评价、确认排期、改变确定性评分、展示隐藏思维链。

当前仅建立契约，尚未执行该节点。
