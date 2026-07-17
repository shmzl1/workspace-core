# seed 数据说明

本目录保存 Sprint 1 演示种子数据。当前不得提交真实个人信息、真实企业数据、真实简历、真实薪资或真实考勤记录。

`policy_documents.json` 是例外：其中不包含企业内部制度或个人信息，只保存经国家法律法规数据库、国家行政法规库和人力资源社会保障部规章库核验的公开现行劳动政策元数据、摘要与官方原文 URL。

当前演示种子数据覆盖：

- 用户；
- 员工；
- 岗位；
- 候选人；
- 面试官；
- 会议室；
- 薪资；
- 年假；
- 考勤记录；
- 公开现行劳动政策；
- 招聘岗位与候选人基础排序数据。

所有样例均使用虚构身份与虚构公司背景。`scripts/build-demo-data.py` 提供可重复重建演示数据的导入入口，但需要人工在已完成数据库迁移和本地环境准备后执行。

仅同步政策、保留其他业务表数据时，在仓库根目录执行：

```powershell
python scripts/seed_policy_documents.py
```

仅为已有候选人申请幂等补全演示面试可用时间、并保留其他业务数据时，在仓库根目录执行：

```powershell
python scripts/seed_interview_availability.py
```

该命令只为没有有效未来 `CANDIDATE` 时段的候选人补充数据。候选人时段来自启用面试官和
启用会议室不少于 60 分钟的未来未占用交集；已有人工时段、禁用时段和其他业务数据不会被修改。
如果面试官或会议室缺少有效时段，命令会回滚并明确报错。

如果 Windows 环境尚未安装项目 Python 依赖，但已经安装 PostgreSQL `psql` 客户端，也可执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/seed-policy-data.ps1
```

这两个命令都按 `document_code` 幂等新增或更新政策，不删除其他政策或业务数据。完整演示数据重建流程 `scripts/seed_dev_data.py` 也会导入同一份政策数据，但会按既有设计清理并重建演示数据，不能用于保留现有业务数据的场景。
