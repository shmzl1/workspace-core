
# TalentFlow DevOps 使用记录

## 1. DevOps 工作流程

项目采用 GitLab 进行代码托管、Issue 管理、分支管理、
合并请求审查和 CI/CD 流水线执行。

基本流程：

1. 在 GitLab Issue 中登记开发任务。
2. 组员在 dev 分支完成日常开发。
3. 提交代码后自动触发 GitLab CI 流水线。
4. 流水线执行后端语法检查、前端配置检查和项目结构检查。
5. 流水线生成当前版本源码制品和 DevOps 执行记录。
6. 稳定版本通过 Merge Request 从 dev 合并至 main。
7. main 分支再次运行流水线，形成稳定版本验收记录。

## 2. CI/CD 阶段

| 阶段    | Job                      | 作用                        |
| ------- | ------------------------ | --------------------------- |
| verify  | backend_syntax_check     | 检查后端 Python 文件语法    |
| verify  | frontend_structure_check | 检查前端工程及 package.json |
| verify  | project_structure_check  | 检查主要项目目录完整性      |
| package | package_source           | 打包当前版本源码制品        |
| record  | devops_record            | 生成本次流水线执行记录      |

## 3.验收证据

验收时保留以下 GitLab 页面截图：

1. Build / Pipelines 流水线列表。
2. Pipeline 详细阶段图。
3. backend_syntax_check 执行日志。
4. frontend_structure_check 执行日志。
5. package_source 生成的 Artifacts。
6. devops_record 生成的 Markdown 记录。
7. dev 合并至 main 的 Merge Request。
8. 对应 Issue、Commit 和合并记录。
