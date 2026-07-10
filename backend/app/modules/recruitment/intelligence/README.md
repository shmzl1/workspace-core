# 招聘 Intelligence 契约

本目录描述简历提取、技能标准化、证据验证、岗位 Rubric 和可信度的纯数据边界，不实现解析、匹配、评分或模型调用。确定性评分仍由现有 Recruitment Service 经公开边界调用禁飞区算法。

- `schemas.py` 是计划中的结构化数据统一入口，并重导出现有契约类型。
- `contracts.py` 保留基础数据契约，避免旧 import 失效。
- 其余模块仅定义 Protocol，不包含真实算法。

当前状态：已建立目录或契约。
